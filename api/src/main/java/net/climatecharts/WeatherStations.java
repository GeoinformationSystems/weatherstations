package net.climatecharts;

import javax.servlet.ServletContext;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.sql.*;
import java.util.ArrayList;
import java.util.Collections;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Weatherstations API for ClimateCharts server. Answers requests from the
 * climatecharts webapp towards the weatherstations.
 *
 * @author Marcus Kossatz
 */

@Path("")
public class WeatherStations {
    /**
     * SQL queries. Parameters use ?-placeholders and are bound via
     * PreparedStatement to avoid SQL injection (stationId comes from a
     * query parameter).
     */
    private static final String SQL_ALL_STATIONS =
        "SELECT * FROM populate_db_station"
        + " WHERE original = TRUE AND complete_data_rate > 0.0";
    private static final String SQL_STATION_DATA =
        "SELECT * FROM populate_db_stationdata"
        + " WHERE station_id = ? AND year >= ? AND year < ?";

    private static final Logger log = Logger.getLogger(WeatherStations.class.getName());

    /**
     * Database connection parameters are read at request time from the
     * servlet context (configured in web.xml "context-param" entries
     * and overridable per deployment via Tomcat context.xml).
     */

    @Context
    ServletContext servletContext;

    @GET
    @Produces(MediaType.TEXT_HTML)
    public Response viewHome() {
        File indexFile = new File(servletContext.getRealPath("/"), "index.html");
        if (!indexFile.isFile()) {
            log.warning("index.html not found at " + indexFile.getAbsolutePath());
            return Response.status(Response.Status.NOT_FOUND).build();
        }
        try {
            // Jersey closes the stream after writing the response.
            return Response.ok(new FileInputStream(indexFile)).build();
        } catch (FileNotFoundException e) {
            // isFile() above should have caught this — defensive only.
            log.warning("index.html disappeared between check and read: " + e.getMessage());
            return Response.status(Response.Status.NOT_FOUND).build();
        }
    }

    /**
     * Public member functions that answer requests to the database
     */

    @GET
    @Path("/getAllStations")
    @Produces("application/json")
    public String getAllStations() {
        var weatherstations = new JSONArray();
        try (var conn = connectToDatabase();
             var statement = conn.createStatement();
             var results = statement.executeQuery(SQL_ALL_STATIONS)) {
            while (results.next()) {
                var newStation = new JSONObject();
                newStation.put("id", results.getString("id"));
                newStation.put("name", results.getString("name"));
                newStation.put("country", results.getString("country"));
                newStation.put("lat", results.getFloat("lat"));
                newStation.put("lng", results.getFloat("lng"));
                newStation.put("elev", results.getInt("elev"));
                newStation.put("min_year", results.getInt("min_year"));
                newStation.put("max_year", results.getInt("max_year"));
                newStation.put("missing_months", results.getInt("missing_months"));
                newStation.put("complete_data_rate", results.getInt("complete_data_rate"));
                newStation.put("largest_gap", results.getInt("largest_gap"));
                weatherstations.put(newStation);
            }
        } catch (SQLException e) {
            log.log(Level.SEVERE, "Failed to load stations", e);
            throw new IllegalStateException("Failed to load stations", e);
        }
        return weatherstations.toString();
    }

    @GET
    @Path("/getStationData")
    @Produces("application/json")
    public String getStationData(@QueryParam("stationId") String stationId, @QueryParam("minYear") int minYear,
                                 @QueryParam("maxYear") int maxYear) {
        if (maxYear <= minYear) {
            throw new IllegalArgumentException(
                "maxYear must be greater than minYear (got minYear=" + minYear
                + ", maxYear=" + maxYear + ")");
        }

        /*
         * data structure: { numYears: number of years prec: for each dataset [ for each
         * month { rawData: [] data for each year mean: data mean by month numGaps:
         * number of missing years }, {...} for each month ], temp: [...] for each
         * dataset }
         */

        int numYears = maxYear - minYear;

        // use 'Float' instead of 'float' to have 'null' as the default value instead of
        // '0.0'
        // --> distinguish between 'null' and '0.0'
        var rawPrecData = new Float[12][numYears];
        var rawTempData = new Float[12][numYears];

        try (var conn = connectToDatabase();
             var statement = conn.prepareStatement(SQL_STATION_DATA)) {
            statement.setString(1, stationId);
            statement.setInt(2, minYear);
            statement.setInt(3, maxYear);
            try (var results = statement.executeQuery()) {
                while (results.next()) {
                    int year = results.getInt("year");
                    int month = results.getInt("month");
                    Float temp = results.getFloat("temperature");
                    if (results.wasNull())
                        temp = null;
                    Float prec = results.getFloat("precipitation");
                    if (results.wasNull())
                        prec = null;

                    rawPrecData[month - 1][year - minYear] = prec;
                    rawTempData[month - 1][year - minYear] = temp;
                }
            }
        } catch (SQLException e) {
            log.log(Level.SEVERE, "Failed to load data for station " + stationId, e);
            throw new IllegalStateException(
                "Failed to load data for station " + stationId, e);
        }

        // create final JSON object structure
        var precData = new JSONArray();
        var tempData = new JSONArray();

        // calculate means and number of gaps
        // for each month
        for (int monthIdx = 0; monthIdx < 12; monthIdx++) {
            // for each dataset
            for (int ds = 0; ds < 2; ds++) {
                // 0 = temperature, 1 = precipitation
                var series = switch (ds) {
                    case 0 -> new MonthData(rawTempData[monthIdx], tempData);
                    default -> new MonthData(rawPrecData[monthIdx], precData);
                };
                Float[] yearlyValues = series.yearlyValues();
                JSONArray outputData = series.outputData();

                // sum up values for each year in this month
                // count the gaps and values to calculate mean and determine the quality
                float sum = 0.0f;
                var median_calculations_list = new ArrayList<Float>();
                int numValues = 0;
                int numGaps = 0;
                for (int yearIdx = 0; yearIdx < numYears; yearIdx++) {
                    Float value = yearlyValues[yearIdx];
                    if (value == null)
                        numGaps++;
                    else {
                        sum += value;
                        median_calculations_list.add(value);
                        numValues++;
                    }
                }

                // calculate mean & median
                Float mean = null;
                Float median = null;
                if (numValues > 0) {
                    // mean
                    mean = sum / numValues;
                    //median
                    Collections.sort(median_calculations_list);
                    int middle = median_calculations_list.size() / 2;
                    if (median_calculations_list.size() % 2 == 0)
                    {
                        float left = median_calculations_list.get(middle - 1);
                        float right = median_calculations_list.get(middle);
                        median = (left + right) / 2;
                    }
                    else
                    {
                        median =  median_calculations_list.get(middle);
                    }
                }

                // write data
                var thisMonth = new JSONObject();
                thisMonth.put("rawData", yearlyValues);
                thisMonth.put("mean", mean);
                thisMonth.put("median", median);
                thisMonth.put("month", monthIdx + 1);
                thisMonth.put("numGaps", numGaps);

                outputData.put(thisMonth);
            }
        }

        var stationData = new JSONObject();
        stationData.put("numYears", numYears);
        stationData.put("minYear", minYear);
        stationData.put("maxYear", maxYear);
        stationData.put("prec", precData);
        stationData.put("temp", tempData);

        return stationData.toString();

    }

    /**
     * Helper functions
     */
    private String dbConfig(String key) {
        String value = servletContext.getInitParameter(key);
        if (value == null) {
            log.severe("Missing required <context-param>: " + key);
            throw new IllegalStateException(
                "Missing required <context-param>: " + key
                + ". Configure it in web.xml or override via Tomcat context.xml.");
        }
        return value;
    }

    /**
     * Package-private to allow unit tests to override and inject a mocked
     * {@link Connection} without needing a running PostgreSQL instance.
     */
    Connection connectToDatabase() {
        String url = String.format("jdbc:postgresql://%s:%s/%s",
            dbConfig("db.host"),
            dbConfig("db.port"),
            dbConfig("db.name"));
        String user = dbConfig("db.user");
        String password = dbConfig("db.password");
        if (password.isEmpty()) {
            throw new IllegalStateException(
                "db.password must not be empty. "
                + "Set it in web.xml or override via Tomcat context.xml.");
        }
        try {
            Class.forName("org.postgresql.Driver");
            return DriverManager.getConnection(url, user, password);
        } catch (ClassNotFoundException e) {
            log.log(Level.SEVERE, "PostgreSQL JDBC driver not found", e);
            throw new IllegalStateException("PostgreSQL JDBC driver not found", e);
        } catch (SQLException e) {
            log.log(Level.SEVERE, "Cannot connect to database at " + url, e);
            throw new IllegalStateException(
                "Cannot connect to database at " + url, e);
        }
    }

    /** Bundles the monthly values and the output JSON array that should
     *  receive them — used as the return type of a switch expression in
     *  {@link #getStationData}. */
    private record MonthData(Float[] yearlyValues, JSONArray outputData) {}
}
