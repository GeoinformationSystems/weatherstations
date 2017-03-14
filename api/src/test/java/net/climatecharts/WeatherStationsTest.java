package net.climatecharts;

import java.io.IOException;

import org.apache.http.ParseException;
import org.junit.Test;

public class WeatherStationsTest
{
	// Test: Weimar
	long stationID = 61710555000L;
	
	// Test: time frame 1980 to 2010
	int minYear = 1950;
	int maxYear = 1980;
	
	@Test
	public void testAllStations() throws ParseException, IOException
	{
		String responseString = new WeatherStations().getAllStations();
		System.out.println(responseString.substring(0, 512));	
	}
	
	@Test
	public void testStationData() throws ParseException, IOException
	{
		String responseString = new WeatherStations().getStationData(stationID, minYear, maxYear);
		System.out.println(responseString.substring(0, 512));	
	}
}
