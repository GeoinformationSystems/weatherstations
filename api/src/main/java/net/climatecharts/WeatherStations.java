package net.climatecharts;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;

import org.json.JSONArray;
import org.json.JSONObject;

import java.sql.*;
import java.util.*;

/**
 * Weatherstations API for ClimateCharts server.
 * Answers requests from the climatecharts webapp towards the weatherstations.
 * 
 * @author Marcus Kossatz
 */

@Path("/{op}")
public class WeatherStations
{	
	/**
	 * CONSTANTS: Database connection data
	 */
	
	private static final String DB_HOST = "127.0.0.1";
	private static final String DB_NAME = "climatecharts_weatherstations";
	private static final String DB_USER = "postgres";
	private static final String DB_PSWD = "postgres";

	
	/**
	 * Public member functions that answer requests to the database
	 */
	
	@GET
	@Produces("application/json")
	public String getAllStations()
	{
		// access the database
		Connection conn = connectToDatabase();
		
		// get all stations
		JSONArray weatherstations = new JSONArray();
		
		try
		{
			Statement statement = conn.createStatement();
			ResultSet results = statement.executeQuery(getAllStationsQuery());
			while(results.next())
			{
				JSONObject newStation = new JSONObject();
				newStation.put("id", 					results.getLong		("id"));
				newStation.put("name",					results.getString	("name"));
				newStation.put("country",				results.getString	("country"));
				newStation.put("lat",					results.getFloat	("lat"));
				newStation.put("lng",					results.getFloat	("lng"));
				newStation.put("elev",					results.getInt		("elev"));
				newStation.put("min_year",				results.getInt		("min_year"));
				newStation.put("max_year",				results.getInt		("max_year"));
				newStation.put("missing_months",		results.getInt		("missing_months"));
				newStation.put("complete_data_rate",	results.getInt		("complete_data_rate"));
				newStation.put("largest_gap",			results.getInt		("largest_gap"));
				weatherstations.put(newStation);
			}
			results.close();
			statement.close();
		}
		catch (SQLException e)
		{
		 	System.err.println("Error in execution of the SQL Statement");
			System.err.println(e.getMessage());
		}
		
		// format them into a JSON string and return
		return weatherstations.toString();
	}
	
	
	@GET
	@Produces("application/json")
	public String getStationData(long stationId, int minYear, int maxYear)
	{
		// access the database
		Connection conn = connectToDatabase();
		
		// data structure: for each year: [temperature[], precipitation[]]
		int numYears = maxYear-minYear;
		float[][][] stationData = new float[numYears][][];
		for (int i=0; i<numYears; i++)
		{
			stationData[i] = new float[2][];
			stationData[i][0] = new float[12];	// temperature
			stationData[i][1] = new float[12];	// precipitation
		}

		// fill data structure
		try
		{
			Statement statement = conn.createStatement();
			ResultSet results = statement.executeQuery(getStationDataQuery(stationId, minYear, maxYear));
			while(results.next())
			{
				int year =				results.getInt		("year");
				int month =				results.getInt		("month");
				float temperature = 	results.getFloat	("temperature");
				float precipitation = 	results.getFloat	("precipitation");
				
				int yearIdx = year-minYear;
				int monthIdx = month-1;
				
				stationData[yearIdx][0][monthIdx] = temperature;
				stationData[yearIdx][1][monthIdx] = precipitation;
			}
			results.close();
			statement.close();
		}
		catch (SQLException e)
		{
		 	System.err.println("Error in execution of the SQL Statement");
			System.err.println(e.getMessage());
		}
		
		// finally transform data structure to JSON
		JSONArray stationDataFinal = new JSONArray();

		// create structure: [{year, 12x precipitation, 12x temperature}]
		for (int i=0; i<numYears; i++)
		{
			JSONObject dataYear = new JSONObject();
			dataYear.put("year", minYear+i);
			dataYear.put("temp", stationData[i][0]);
			dataYear.put("prec", stationData[i][1]);
			stationDataFinal.put(dataYear);
		}

		// format result in a JSON string and return
		return stationDataFinal.toString();
	}
	
	/**
	 * Helper functions
	 */
	private Connection connectToDatabase()
	{
		Connection conn = null;
		try
		{
			Class.forName("org.postgresql.Driver");
			String url = "jdbc:postgresql://" + DB_HOST + "/" + DB_NAME;
			conn = DriverManager.getConnection(url, DB_USER, DB_PSWD);
		}
		catch (ClassNotFoundException e)
		{
			e.printStackTrace();
			System.exit(1);
		}
		catch (SQLException e)
		{
			e.printStackTrace();
			System.exit(2);
		}
		return conn;
	}
	
	private String getAllStationsQuery()
	{
		return "SELECT * FROM populate_db_station";
	}
	
	private String getStationDataQuery(long stationId, int minYear, int maxYear)
	{
		return "SELECT * FROM populate_db_stationdata WHERE station_id="
			+ stationId
			+ " AND year>="
			+ minYear
			+ " AND year<"
			+ maxYear;
	}
}
