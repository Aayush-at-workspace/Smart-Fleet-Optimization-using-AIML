import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Car, 
  MapPin, 
  Clock, 
  Users, 
  Zap, 
  TrendingUp,
  Target,
  Navigation
} from 'lucide-react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import axios from 'axios';
import toast from 'react-hot-toast';
import './FleetOptimization.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const FleetOptimization = () => {
  const [zones, setZones] = useState([]);
  const [formData, setFormData] = useState({
    pickup: '',
    drop: '',
    pickup_time: '',
    drop_time: '',
    passengers: 1
  });
  const [loading, setLoading] = useState(false);
  const [optimizationResults, setOptimizationResults] = useState(null);
  const [selectedZone, setSelectedZone] = useState(null);
  const resultsRef = React.useRef(null);

  useEffect(() => {
    fetchZones();
  }, []);

  const fetchZones = async () => {
    try {
      const response = await axios.get('/zones');
      setZones(response.data.zones);
    } catch (error) {
      console.error('Error fetching zones:', error);
      toast.error('Failed to fetch zones');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post('/complete_ride', formData);
      
      if (response.data?.new_ride) {
        toast.success('Ride completed successfully!');

        // Use backend recommendations directly if present
        const recs = Array.isArray(response.data.recommendations) ? response.data.recommendations : [];
        const zonesPayload = recs.map(r => ({
          id: r.id,
          name: r.name,
          probability: r.probability,
          distance: Math.round(r.distance)
        }));

        setOptimizationResults({ zones: zonesPayload });
        // Smooth scroll to results
        setTimeout(() => {
          resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 50);
      }
    } catch (error) {
      console.error('Error completing ride:', error);
      toast.error(error.response?.data?.error || 'Failed to complete ride');
    } finally {
      setLoading(false);
    }
  };

  const formatDistance = (meters) => {
    if (meters == null || isNaN(meters)) return '-';
    if (meters >= 1000) return (meters / 1000).toFixed(1) + ' km';
    return Math.round(meters) + ' m';
  };

  const chartData = {
    labels: optimizationResults?.zones.map(zone => zone.name) || [],
    datasets: [
      {
        label: 'Probability',
        data: optimizationResults?.zones.map(zone => zone.probability) || [],
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
        borderRadius: 8,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: true,
        text: 'Zone Probability Distribution',
        color: 'var(--text-primary)',
        font: {
          size: 16,
          weight: '600'
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1,
        ticks: {
          color: 'var(--text-secondary)',
          callback: function(value) {
            return (value * 100).toFixed(0) + '%';
          }
        },
        grid: {
          color: 'var(--border)'
        }
      },
      x: {
        ticks: {
          color: 'var(--text-secondary)'
        },
        grid: {
          color: 'var(--border)'
        }
      }
    }
  };

  return (
    <motion.div 
      className="fleet-optimization"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <div className="optimization-header">
        <motion.div
          initial={{ x: -50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="page-title">
            <Zap className="title-icon" />
            Fleet Optimization
          </h1>
          <p className="page-subtitle">
            AI-powered route optimization and demand prediction for maximum fleet efficiency
          </p>
        </motion.div>
      </div>

      <div className="optimization-content">
        {/* Ride Form */}
        <motion.div 
          className="ride-form-section"
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="form-card card">
            <div className="form-header">
              <Car className="form-icon" />
              <h2>Complete New Ride</h2>
              <p>Enter ride details to trigger fleet optimization</p>
            </div>
            
            <form onSubmit={handleSubmit} className="ride-form">
              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">
                    <MapPin className="label-icon" />
                    Pickup Location
                  </label>
                  <select
                    name="pickup"
                    value={formData.pickup}
                    onChange={handleInputChange}
                    className="form-input"
                    required
                  >
                    <option value="">Select pickup zone...</option>
                    {zones.map(zone => (
                      <option key={zone.id} value={zone.zone}>
                        {zone.zone} ({zone.borough})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">
                    <Target className="label-icon" />
                    Drop Location
                  </label>
                  <select
                    name="drop"
                    value={formData.drop}
                    onChange={handleInputChange}
                    className="form-input"
                    required
                  >
                    <option value="">Select drop zone...</option>
                    {zones.map(zone => (
                      <option key={zone.id} value={zone.zone}>
                        {zone.zone} ({zone.borough})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">
                    <Clock className="label-icon" />
                    Pickup Time
                  </label>
                  <input
                    type="datetime-local"
                    name="pickup_time"
                    value={formData.pickup_time}
                    onChange={handleInputChange}
                    className="form-input"
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">
                    <Navigation className="label-icon" />
                    Drop Time
                  </label>
                  <input
                    type="datetime-local"
                    name="drop_time"
                    value={formData.drop_time}
                    onChange={handleInputChange}
                    className="form-input"
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">
                    <Users className="label-icon" />
                    Passengers
                  </label>
                  <input
                    type="number"
                    name="passengers"
                    value={formData.passengers}
                    onChange={handleInputChange}
                    min="1"
                    max="6"
                    className="form-input"
                    required
                  />
                </div>
              </div>

              <motion.button
                type="submit"
                className="btn btn-primary submit-btn"
                disabled={loading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {loading ? (
                  <>
                    <div className="loading-spinner" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Zap />
                    Complete Ride & Optimize
                  </>
                )}
              </motion.button>
            </form>
          </div>
        </motion.div>

        {/* Optimization Results */}
        <AnimatePresence>
          {optimizationResults && (
            <motion.div 
              className="optimization-results"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ duration: 0.6 }}
            >
              <div className="results-header">
                <TrendingUp className="results-icon" />
                <h2>Optimization Results</h2>
                <p>Top {optimizationResults?.zones?.length || 0} recommended zones based on AI analysis</p>
                <div className="scroll-hint" onClick={() => resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })}>
                  ↓ Scroll to see recommendations
                </div>
              </div>

              <div className="results-grid">
                {/* Probability Chart */}
                <div className="chart-card card">
                  <h3>Zone Probability Distribution</h3>
                  <div className="chart-container">
                    <Bar data={chartData} options={chartOptions} />
                  </div>
                </div>

                {/* Zone Recommendations */}
                <div className="recommendations-card card" ref={resultsRef}>
                  <h3>Recommended Zones</h3>
                  <div className="recommendations-list">
                    {optimizationResults.zones.map((zone, index) => (
                      <motion.div
                        key={zone.id}
                        className={`recommendation-item rank-${index + 1}`}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        whileHover={{ scale: 1.02 }}
                        onClick={() => setSelectedZone(zone)}
                      >
                        <div className="rank-badge">{index + 1}</div>
                        <div className="zone-info">
                          <h4 className="zone-name">{zone.name}</h4>
                          <div className="zone-metrics">
                            <span className="probability">
                              {(zone.probability * 100).toFixed(1)}% probability
                            </span>
                            <span className="distance">
                              {formatDistance(zone.distance)} away
                            </span>
                          </div>
                        </div>
                        <div className="zone-actions">
                          <button className="btn btn-accent btn-sm">
                            <Navigation />
                            Navigate
                          </button>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Selected Zone Details */}
              {selectedZone && (
                <motion.div 
                  className="zone-details card"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="zone-details-header">
                    <h3>Zone Details: {selectedZone.name}</h3>
                    <button 
                      className="close-btn"
                      onClick={() => setSelectedZone(null)}
                    >
                      ×
                    </button>
                  </div>
                  <div className="zone-details-content">
                    <div className="detail-item">
                      <span className="detail-label">Probability Score:</span>
                      <span className="detail-value">
                        {(selectedZone.probability * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Distance:</span>
                      <span className="detail-value">{selectedZone.distance}m</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Demand Level:</span>
                      <span className="detail-value high">High</span>
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default FleetOptimization;
