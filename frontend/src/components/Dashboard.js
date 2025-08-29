import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  Car, 
  TrendingUp, 
  MapPin, 
  Clock, 
  Zap,
  BarChart3,
  ArrowRight,
  Activity,
  Target,
  Shield,
  Globe
} from 'lucide-react';
import './Dashboard.css';

const Dashboard = () => {
  const stats = [
    {
      title: 'Total Zones',
      value: '263',
      change: '+2.5%',
      icon: MapPin,
      color: 'var(--primary)',
      trend: 'up'
    },
    {
      title: 'Active Trips',
      value: '10.2M',
      change: '+12.3%',
      icon: Car,
      color: 'var(--success)',
      trend: 'up'
    },
    {
      title: 'Fleet Efficiency',
      value: '94.2%',
      change: '+5.1%',
      icon: TrendingUp,
      color: 'var(--accent)',
      trend: 'up'
    },
    {
      title: 'Response Time',
      value: '2.3min',
      change: '-8.7%',
      icon: Clock,
      color: 'var(--secondary)',
      trend: 'down'
    }
  ];

  const features = [
    {
      title: 'AI-Powered Optimization',
      description: 'Machine learning algorithms optimize fleet routes and reduce idle time',
      icon: Zap,
      color: 'var(--primary)',
      link: '/optimization'
    },
    {
      title: 'Real-time Analytics',
      description: 'Monitor fleet performance with live dashboards and insights',
      icon: BarChart3,
      color: 'var(--secondary)',
      link: '/analytics'
    },
    {
      title: 'Smart Zone Management',
      description: 'Intelligent zone allocation based on demand patterns',
      icon: Target,
      color: 'var(--accent)',
      link: '/optimization'
    },
    {
      title: 'Predictive Maintenance',
      description: 'AI-driven maintenance scheduling to prevent breakdowns',
      icon: Shield,
      color: 'var(--success)',
      link: '/analytics'
    }
  ];

  const recentActivity = [
    { action: 'New ride completed', zone: 'Manhattan', time: '2 min ago', status: 'success' },
    { action: 'Fleet optimization applied', zone: 'Brooklyn', time: '5 min ago', status: 'info' },
    { action: 'Demand prediction updated', zone: 'Queens', time: '12 min ago', status: 'warning' },
    { action: 'New zone added', zone: 'Bronx', time: '1 hour ago', status: 'success' }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <motion.div 
      className="dashboard"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Hero Section */}
      <motion.section 
        className="hero-section"
        variants={itemVariants}
      >
        <div className="hero-content">
          <h1 className="hero-title">
            Welcome to <span className="gradient-text">Smart Fleet</span>
          </h1>
          <p className="hero-subtitle">
            AI-powered fleet optimization system that revolutionizes urban transportation
          </p>
          <div className="hero-actions">
            <Link to="/optimization" className="btn btn-primary">
              <Zap />
              Start Optimization
            </Link>
            <Link to="/analytics" className="btn btn-secondary">
              <BarChart3 />
              View Analytics
            </Link>
          </div>
        </div>
        <div className="hero-visual">
          <motion.div 
            className="floating-elements"
            animate={{ 
              y: [0, -20, 0],
              rotate: [0, 5, 0]
            }}
            transition={{ 
              duration: 6,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            <div className="floating-card card-1">
              <Car />
              <span>Smart Routing</span>
            </div>
            <div className="floating-card card-2">
              <Activity />
              <span>Real-time Data</span>
            </div>
            <div className="floating-card card-3">
              <Globe />
              <span>Global Coverage</span>
            </div>
          </motion.div>
        </div>
      </motion.section>

      {/* Stats Grid */}
      <motion.section 
        className="stats-section"
        variants={itemVariants}
      >
        <h2 className="section-title">System Overview</h2>
        <div className="stats-grid">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.title}
              className="stat-card card"
              variants={itemVariants}
              whileHover={{ y: -8, scale: 1.02 }}
            >
              <div className="stat-header">
                <div 
                  className="stat-icon-wrapper"
                  style={{ backgroundColor: `${stat.color}20` }}
                >
                  <stat.icon style={{ color: stat.color }} />
                </div>
                <div className="stat-change">
                  <span className={`trend-${stat.trend}`}>
                    {stat.change}
                  </span>
                </div>
              </div>
              <div className="stat-content">
                <h3 className="stat-value">{stat.value}</h3>
                <p className="stat-title">{stat.title}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Features Grid */}
      <motion.section 
        className="features-section"
        variants={itemVariants}
      >
        <h2 className="section-title">Key Features</h2>
        <div className="features-grid">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              className="feature-card card"
              variants={itemVariants}
              whileHover={{ y: -8, scale: 1.02 }}
            >
              <div 
                className="feature-icon"
                style={{ color: feature.color }}
              >
                <feature.icon />
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
              <Link to={feature.link} className="feature-link">
                Learn More <ArrowRight />
              </Link>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Recent Activity */}
      <motion.section 
        className="activity-section"
        variants={itemVariants}
      >
        <h2 className="section-title">Recent Activity</h2>
        <div className="activity-card card">
          <div className="activity-list">
            {recentActivity.map((activity, index) => (
              <motion.div
                key={index}
                className="activity-item"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="activity-content">
                  <span className="activity-action">{activity.action}</span>
                  <span className="activity-zone">in {activity.zone}</span>
                </div>
                <div className="activity-meta">
                  <span className="activity-time">{activity.time}</span>
                  <span className={`activity-status status-${activity.status}`}>
                    {activity.status}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>
    </motion.div>
  );
};

export default Dashboard;
