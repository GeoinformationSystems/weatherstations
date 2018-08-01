package net.climatecharts;

import javax.servlet.ServletContext;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.sql.*;

/**
 * Weatherstations API for ClimateCharts server. Answers requests from the
 * climatecharts webapp towards the weatherstations.
 *
 * @author Marcus Kossatz
 */

@Path("")
public class WeatherStations {
    /**
     * CONSTANTS: Database connection data
     */

    private static final String DB_HOST = "127.0.0.1";
    private static final String DB_NAME = "climatecharts_weatherstations";
    private static final String DB_USER = "postgres";
    private static final String DB_PSWD = "postgres";

    @Context
    ServletContext servletContext;

    @GET
    @Produces({MediaType.TEXT_HTML})
    public InputStream viewHome() {
        try {
            String base = servletContext.getRealPath("/");
            File f = new File(String.format("%s/%s", base, "index.html"));
            return new FileInputStream(f);
        } catch (FileNotFoundException e) {
            return null;
        }
    }

    /**
     * Public member functions that answer requests to the database
     */

    @GET
    @Path("/getAllStations")
    @Produces("application/json")
    public String getAllStations() {
        // access the database
        Connection conn = connectToDatabase();

        // get all stations
        JSONArray weatherstations = new JSONArray();

        try {
            Statement statement = conn.createStatement();
            ResultSet results = statement.executeQuery(getAllStationsQuery());
            while (results.next()) {
                JSONObject newStation = new JSONObject();
                newStation.put("id", results.getLong("id"));
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
            results.close();
            statement.close();
        } catch (SQLException e) {
            System.err.println("Error in execution of the SQL Statement");
            System.err.println(e.getMessage());
        }

        // format them into a JSON string and return
        return weatherstations.toString();
    }

    @GET
    @Path("/getStationData")
    @Produces("application/json")
    public String getStationData(@QueryParam("stationId") long stationId, @QueryParam("minYear") int minYear,
                                 @QueryParam("maxYear") int maxYear) {
        // access the database
        Connection conn = connectToDatabase();

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
        Float[][] rawPrecData = new Float[12][numYears];
        Float[][] rawTempData = new Float[12][numYears];

        try {
            Statement statement = conn.createStatement();
            ResultSet results = statement.executeQuery(getStationDataQuery(stationId, minYear, maxYear));
            while (results.next()) {
                int year = results.getInt("year");
                int month = results.getInt("month");
                float temp = results.getFloat("temperature");
                float prec = results.getFloat("precipitation");

                int yearIdx = year - minYear;
                int monthIdx = month - 1;

                rawPrecData[monthIdx][yearIdx] = prec;
                rawTempData[monthIdx][yearIdx] = temp;

            }
            results.close();
            statement.close();
        } catch (SQLException e) {
            System.err.println("Error in execution of the SQL Statement");
            System.err.println(e.getMessage());
        }

        // create final JSON object structure
        JSONArray precData = new JSONArray();
        JSONArray tempData = new JSONArray();

        // calculate means and number of gaps
        // for each month
        for (int monthIdx = 0; monthIdx < 12; monthIdx++) {
            // for each dataset
            for (int ds = 0; ds < 2; ds++) {
                Float[] yearlyValues;
                JSONArray outputData;
                if (ds == 0) // temperature
                {
                    yearlyValues = rawTempData[monthIdx];
                    outputData = tempData;
                } else // precipitation
                {
                    yearlyValues = rawPrecData[monthIdx];
                    outputData = precData;
                }

                // sum up values for each year in this month
                // count the gaps and values to calculate mean and determine the quality
                float sum = 0.0f;
                int numValues = 0;
                int numGaps = 0;
                for (int yearIdx = 0; yearIdx < numYears; yearIdx++) {
                    Float value = yearlyValues[yearIdx];
                    if (value == null)
                        numGaps++;
                    else {
                        sum += value;
                        numValues++;
                    }
                }

                // calculate mean
                Float mean = null;
                if (numValues > 0)
                    mean = sum / numValues;

                // write data
                JSONObject thisMonth = new JSONObject();
                thisMonth.put("rawData", yearlyValues);
                thisMonth.put("mean", mean);
                thisMonth.put("numGaps", numGaps);

                outputData.put(thisMonth);
            }
        }

        JSONObject stationData = new JSONObject();
        stationData.put("numYears", numYears);
        stationData.put("prec", precData);
        stationData.put("temp", tempData);

        return stationData.toString();

    }

    /**
     * Helper functions
     */
    private Connection connectToDatabase() {
        Connection conn = null;
        try {
            Class.forName("org.postgresql.Driver");
            String url = "jdbc:postgresql://" + DB_HOST + "/" + DB_NAME;
            conn = DriverManager.getConnection(url, DB_USER, DB_PSWD);
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
            System.exit(1);
        } catch (SQLException e) {
            e.printStackTrace();
            System.exit(2);
        }
        return conn;
    }

    private String getAllStationsQuery() {
        return "SELECT * FROM populate_db_station WHERE original = TRUE";
    }

    private String getStationDataQuery(long stationId, int minYear, int maxYear) {
        return "SELECT * FROM populate_db_stationdata WHERE station_id=" + stationId + " AND year>=" + minYear
                + " AND year<" + maxYear;
    }
}
