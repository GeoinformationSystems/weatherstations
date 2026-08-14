package net.climatecharts;

import org.junit.Before;
import org.junit.Test;
import org.mockito.ArgumentCaptor;

import jakarta.servlet.ServletContext;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * Unit tests for {@link WeatherStations} using mocked JDBC and Servlet
 * context. No live PostgreSQL instance is required.
 */
public class WeatherStationsUnitTest
{
	private ServletContext servletContext;
	private Connection conn;
	private PreparedStatement ps;
	private Statement stmt;
	private ResultSet rs;

	private WeatherStations ws;

	@Before
	public void setUp() throws Exception
	{
		servletContext = mock(ServletContext.class);
		conn = mock(Connection.class);
		ps = mock(PreparedStatement.class);
		stmt = mock(Statement.class);
		rs = mock(ResultSet.class);

		// dbConfig() pulls all five values from the servlet context on every request.
		when(servletContext.getInitParameter("db.host")).thenReturn("localhost");
		when(servletContext.getInitParameter("db.port")).thenReturn("5432");
		when(servletContext.getInitParameter("db.name")).thenReturn("test");
		when(servletContext.getInitParameter("db.user")).thenReturn("user");
		when(servletContext.getInitParameter("db.password")).thenReturn("pw");

		// Subclass to inject the mocked Connection without a real DriverManager call.
		ws = new WeatherStations() {
			@Override
			Connection connectToDatabase() {
				return conn;
			}
		};
		ws.servletContext = servletContext;
	}

	// ---------- getStationData ----------

	/**
	 * Regression test for the SQL-injection fix: a malicious stationId must be
	 * passed as a literal parameter to PreparedStatement.setString — never
	 * concatenated into the SQL string.
	 */
	@Test
	public void getStationData_treatsStationIdAsLiteralParameter() throws Exception
	{
		String maliciousId = "' OR '1'='1";

		when(conn.prepareStatement(anyString())).thenReturn(ps);
		when(ps.executeQuery()).thenReturn(rs);
		when(rs.next()).thenReturn(false);

		ws.getStationData(maliciousId, 1980, 2010);

		// Parameters are bound positionally — the malicious input is just a value.
		verify(ps).setString(1, maliciousId);
		verify(ps).setInt(2, 1980);
		verify(ps).setInt(3, 2010);

		// And the SQL string itself contains only placeholders, never user input.
		ArgumentCaptor<String> sqlCaptor = ArgumentCaptor.forClass(String.class);
		verify(conn).prepareStatement(sqlCaptor.capture());
		String sql = sqlCaptor.getValue();
		assertFalse("SQL must not embed user input", sql.contains(maliciousId));
		assertTrue("SQL must use a placeholder for station_id", sql.contains("station_id = ?"));
		assertTrue("SQL must use a placeholder for the lower year bound", sql.contains("year >= ?"));
		assertTrue("SQL must use a placeholder for the upper year bound", sql.contains("year < ?"));
	}

	@Test(expected = IllegalArgumentException.class)
	public void getStationData_rejectsMaxYearLessThanMinYear()
	{
		ws.getStationData("STATION1", 2010, 1980);
	}

	@Test(expected = IllegalArgumentException.class)
	public void getStationData_rejectsEqualYears()
	{
		ws.getStationData("STATION1", 2000, 2000);
	}

	@Test
	public void getStationData_buildsExpectedJsonShape() throws Exception
	{
		when(conn.prepareStatement(anyString())).thenReturn(ps);
		when(ps.executeQuery()).thenReturn(rs);

		// Two result rows for January 1980 and January 1981.
		when(rs.next()).thenReturn(true, true, false);
		when(rs.getInt("year")).thenReturn(1980, 1981);
		when(rs.getInt("month")).thenReturn(1, 1);
		when(rs.getFloat("temperature")).thenReturn(5.0f, 6.0f);
		when(rs.getFloat("precipitation")).thenReturn(50.0f, 60.0f);
		when(rs.wasNull()).thenReturn(false, false, false, false);

		String json = ws.getStationData("STATION1", 1980, 1982);

		assertTrue("numYears field present", json.contains("\"numYears\":2"));
		assertTrue("minYear field present", json.contains("\"minYear\":1980"));
		assertTrue("maxYear field present", json.contains("\"maxYear\":1982"));
		assertTrue("temperature section present", json.contains("\"temp\""));
		assertTrue("precipitation section present", json.contains("\"prec\""));
		// January temperature: two values, mean 5.5, no gaps.
		assertTrue("month 1 mean computed", json.contains("\"mean\":5.5"));
		assertTrue("month 1 rawData populated", json.contains("\"rawData\":[5,6]"));
		assertTrue("month 1 numGaps is 0", json.contains("\"numGaps\":0,\"mean\":5.5"));
		// Months 2..12 have no data — check that the first gap month is reported.
		assertTrue("month 2 rawData is null/null", json.contains("\"rawData\":[null,null]"));
	}

	// ---------- getAllStations ----------

	@Test
	public void getAllStations_buildsExpectedJsonShape() throws Exception
	{
		when(conn.createStatement()).thenReturn(stmt);
		when(stmt.executeQuery(anyString())).thenReturn(rs);

		// Two station rows.
		when(rs.next()).thenReturn(true, true, false);
		when(rs.getString("id")).thenReturn("ST1", "ST2");
		when(rs.getString("name")).thenReturn("Station One", "Station Two");
		when(rs.getString("country")).thenReturn("DE", "FR");
		when(rs.getFloat("lat")).thenReturn(50.0f, 48.0f);
		when(rs.getFloat("lng")).thenReturn(8.0f, 2.0f);
		when(rs.getInt("elev")).thenReturn(100, 200);
		when(rs.getInt("min_year")).thenReturn(1900, 1950);
		when(rs.getInt("max_year")).thenReturn(2020, 2020);
		when(rs.getInt("missing_months")).thenReturn(5, 10);
		when(rs.getInt("complete_data_rate")).thenReturn(95, 90);
		when(rs.getInt("largest_gap")).thenReturn(2, 3);

		String json = ws.getAllStations();

		// All station IDs and names should appear in the output.
		assertTrue("first station id present", json.contains("ST1"));
		assertTrue("second station id present", json.contains("ST2"));
		assertTrue("first station name present", json.contains("Station One"));
		assertTrue("second station name present", json.contains("Station Two"));

		// The SQL selects from the master-station table with the expected filter.
		ArgumentCaptor<String> sqlCaptor = ArgumentCaptor.forClass(String.class);
		verify(stmt).executeQuery(sqlCaptor.capture());
		String sql = sqlCaptor.getValue();
		assertTrue("SQL targets populate_db_station table", sql.contains("populate_db_station"));
		assertTrue("SQL filters master stations", sql.contains("original = TRUE"));
		assertTrue("SQL filters for usable data", sql.contains("complete_data_rate > 0.0"));
	}
}
