package net.climatecharts;

import org.junit.Ignore;
import org.junit.Test;

/**
 * Integration tests that require a running PostgreSQL database
 * reachable with the credentials configured in web.xml.
 *
 * Disabled by default in the unit-test phase.
 */
@Ignore("Integration test — requires a live PostgreSQL database.")
public class WeatherStationsTest
{
	// Test: Dresden
	String stationID = "GMM00010488";

	// Test: time frame 1980 to 2010
	int minYear = 1980;
	int maxYear = 2010;

	@Test
	public void testAllStations()
	{
		String responseString = new WeatherStations().getAllStations();
		System.out.println(responseString.substring(0, 512));
	}

	@Test
	public void testStationData()
	{
		String responseString = new WeatherStations().getStationData(stationID, minYear, maxYear);
		System.out.println(responseString);
	}
}
