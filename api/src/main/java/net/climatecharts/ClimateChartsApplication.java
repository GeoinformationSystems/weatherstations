package net.climatecharts;

import java.util.HashSet;
import java.util.Set;

import javax.ws.rs.ApplicationPath;
import javax.ws.rs.core.Application;

/**
 * Application endpoint for ClimateCharts server
 * 
 * @author marcus
 */

@ApplicationPath("/api")
public class ClimateChartsApplication extends Application
{	
	@Override
	public Set<Class<?>> getClasses()
	{
		final Set<Class<?>> classes = new HashSet<Class<?>>();
		classes.add(WeatherStations.class);
		return classes;
	}
}
