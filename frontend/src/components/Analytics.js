import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  MapPin, 
  Clock, 
  Users,
  Activity,
  Target,
  Zap,
  Calendar
} from 'lucide-react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import './Analytics.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedZone, setSelectedZone] = useState('all');

  // Mock data - replace with real API calls
  const demandTrendData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Demand',
        data: [65, 78, 90, 81, 95, 88, 72],
        borderColor: 'rgb(99, 102, 241)',
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Supply',
        data: [60, 75, 85, 78, 90, 82, 70],
        borderColor: 'rgb(6, 182, 212)',
        backgroundColor: 'rgba(6, 182, 212, 0.1)',
        fill: true,
        tension: 0.4,
      }
    ]
  };

  const zonePerformanceData = {
    labels: ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island'],
    datasets: [
      {
        label: 'Efficiency Score',
        data: [94, 87, 82, 79, 76],
        backgroundColor: [
          'rgba(99, 102, 241, 0.8)',
          'rgba(6, 182, 212, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(239, 68, 68, 0.8)'
        ],
        borderColor: [
          'rgba(99, 102, 241, 1)',
          'rgba(6, 182, 212, 1)',
          'rgba(245, 158, 11, 1)',
          'rgba(16, 185, 129, 1)',
          'rgba(239, 68, 68, 1)'
        ],
        borderWidth: 2,
        borderRadius: 8,
      }
    ]
  };

  const demandDistributionData = {
    labels: ['Peak Hours', 'Off-Peak', 'Night'],
    datasets: [
      {
        data: [45, 35, 20],
        backgroundColor: [
          'rgba(99, 102, 241, 0.8)',
          'rgba(6, 182, 212, 0.8)',
          'rgba(245, 158, 11, 0.8)'
        ],
        borderColor: [
          'rgba(99, 102, 241, 1)',
          'rgba(6, 182, 212, 1)',
          'rgba(245, 158, 11, 1)'
        ],
        borderWidth: 2,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: 'var(--text-primary)',
          usePointStyle: true,
          padding: 20,
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'var(--border)',
        },
        ticks: {
          color: 'var(--text-secondary)',
        }
      },
      x: {
        grid: {
          color: 'var(--border)',
        },
        ticks: {
          color: 'var(--text-secondary)',
        }
      }
    }
  };

  const lineChartOptions = {
    ...chartOptions,
    plugins: {
      ...chartOptions.plugins,
      legend: {
        ...chartOptions.plugins.legend,
        position: 'top',
      }
    }
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: 'var(--text-primary)',
          usePointStyle: true,
          padding: 20,
        }
      }
    }
  };

  const metrics = [
    {
      title: 'Total Trips',
      value: '2.4M',
      change: '+12.5%',
      trend: 'up',
      icon: Activity,
      color: 'var(--primary)'
    },
    {
      title: 'Fleet Efficiency',
      value: '94.2%',
      change: '+5.1%',
      trend: 'up',
      icon: TrendingUp,
      color: 'var(--success)'
    },
    {
      title: 'Avg Response Time',
      value: '2.3min',
      change: '-8.7%',
      trend: 'down',
      icon: Clock,
      color: 'var(--secondary)'
    },
    {
      title: 'Active Drivers',
      value: '1,847',
      change: '+3.2%',
      trend: 'up',
      icon: Users,
      color: 'var(--accent)'
    }
  ];

  const insights = [
    {
      title: 'Peak Demand Pattern',
      description: 'Demand peaks between 7-9 AM and 5-7 PM on weekdays',
      icon: TrendingUp,
      type: 'info'
    },
    {
      title: 'Zone Optimization',
      description: 'Manhattan shows highest efficiency with 94% score',
      icon: Target,
      type: 'success'
    },
    {
      title: 'Supply Gap',
      description: 'Supply lags demand by 8% during peak hours',
      icon: Activity,
      type: 'warning'
    }
  ];

  return (
    <motion.div 
      className="analytics"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <div className="analytics-header">
        <motion.div
          initial={{ x: -50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="page-title">
            <BarChart3 className="title-icon" />
            Analytics Dashboard
          </h1>
          <p className="page-subtitle">
            Comprehensive insights into fleet performance and optimization metrics
          </p>
        </motion.div>

        <motion.div 
          className="analytics-controls"
          initial={{ x: 50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="control-group">
            <label className="control-label">
              <Calendar className="control-icon" />
              Time Range
            </label>
            <select 
              value={timeRange} 
              onChange={(e) => setTimeRange(e.target.value)}
              className="control-select"
            >
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </select>
          </div>

          <div className="control-group">
            <label className="control-label">
              <MapPin className="control-icon" />
              Zone
            </label>
            <select 
              value={selectedZone} 
              onChange={(e) => setSelectedZone(e.target.value)}
              className="control-select"
            >
              <option value="all">All Zones</option>
              <option value="manhattan">Manhattan</option>
              <option value="brooklyn">Brooklyn</option>
              <option value="queens">Queens</option>
              <option value="bronx">Bronx</option>
              <option value="staten-island">Staten Island</option>
            </select>
          </div>
        </motion.div>
      </div>

      {/* Metrics Grid */}
      <motion.section 
        className="metrics-section"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <div className="metrics-grid">
          {metrics.map((metric, index) => (
            <motion.div
              key={metric.title}
              className="metric-card card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -8, scale: 1.02 }}
            >
              <div className="metric-header">
                <div 
                  className="metric-icon-wrapper"
                  style={{ backgroundColor: `${metric.color}20` }}
                >
                  <metric.icon style={{ color: metric.color }} />
                </div>
                <div className="metric-change">
                  <span className={`trend-${metric.trend}`}>
                    {metric.change}
                  </span>
                </div>
              </div>
              <div className="metric-content">
                <h3 className="metric-value">{metric.value}</h3>
                <p className="metric-title">{metric.title}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Charts Section */}
      <motion.section 
        className="charts-section"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <div className="charts-grid">
          {/* Demand Trend Chart */}
          <div className="chart-card card">
            <div className="chart-header">
              <h3>Demand vs Supply Trend</h3>
              <p>Weekly demand and supply patterns</p>
            </div>
            <div className="chart-container">
              <Line data={demandTrendData} options={lineChartOptions} />
            </div>
          </div>

          {/* Zone Performance Chart */}
          <div className="chart-card card">
            <div className="chart-header">
              <h3>Zone Performance</h3>
              <p>Efficiency scores by zone</p>
            </div>
            <div className="chart-container">
              <Bar data={zonePerformanceData} options={chartOptions} />
            </div>
          </div>

          {/* Demand Distribution Chart */}
          <div className="chart-card card">
            <div className="chart-header">
              <h3>Demand Distribution</h3>
              <p>Demand patterns by time of day</p>
            </div>
            <div className="chart-container">
              <Doughnut data={demandDistributionData} options={doughnutOptions} />
            </div>
          </div>
        </div>
      </motion.section>

      {/* Insights Section */}
      <motion.section 
        className="insights-section"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        <h2 className="section-title">Key Insights</h2>
        <div className="insights-grid">
          {insights.map((insight, index) => (
            <motion.div
              key={insight.title}
              className="insight-card card"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -4, scale: 1.02 }}
            >
              <div className="insight-icon">
                <insight.icon />
              </div>
              <h3 className="insight-title">{insight.title}</h3>
              <p className="insight-description">{insight.description}</p>
              <div className={`insight-badge ${insight.type}`}>
                {insight.type}
              </div>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Recommendations Section */}
      <motion.section 
        className="recommendations-section"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.6 }}
      >
        <h2 className="section-title">AI Recommendations</h2>
        <div className="recommendations-card card">
          <div className="recommendation-header">
            <Zap className="recommendation-icon" />
            <h3>Optimization Suggestions</h3>
          </div>
          <div className="recommendation-list">
            <div className="recommendation-item">
              <div className="recommendation-content">
                <h4>Increase Fleet in Manhattan</h4>
                <p>Demand exceeds supply by 15% during peak hours</p>
              </div>
              <div className="recommendation-priority high">High Priority</div>
            </div>
            <div className="recommendation-item">
              <div className="recommendation-content">
                <h4>Optimize Brooklyn Routes</h4>
                <p>Route efficiency can be improved by 8%</p>
              </div>
              <div className="recommendation-priority medium">Medium Priority</div>
            </div>
            <div className="recommendation-item">
              <div className="recommendation-content">
                <h4>Night Shift Optimization</h4>
                <p>Consider reducing night shift drivers by 20%</p>
              </div>
              <div className="recommendation-priority low">Low Priority</div>
            </div>
          </div>
        </div>
      </motion.section>
    </motion.div>
  );
};

export default Analytics;
