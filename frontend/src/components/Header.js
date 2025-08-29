import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Car, 
  BarChart3, 
  Zap, 
  Menu, 
  X,
  TrendingUp,
  MapPin,
  Users
} from 'lucide-react';
import './Header.css';

const Header = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: BarChart3 },
    { path: '/optimization', label: 'Fleet Optimization', icon: Zap },
    { path: '/analytics', label: 'Analytics', icon: TrendingUp },
  ];

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <motion.header 
      className="header"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      <div className="header-container">
        <motion.div 
          className="logo"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Link to="/" className="logo-link">
            <Car className="logo-icon" />
            <span className="logo-text">
              <span className="gradient-text">Smart</span> Fleet
            </span>
          </Link>
        </motion.div>

        <nav className="nav-desktop">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <motion.div
                key={item.path}
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.95 }}
              >
                <Link
                  to={item.path}
                  className={`nav-link ${isActive ? 'active' : ''}`}
                >
                  <Icon className="nav-icon" />
                  <span>{item.label}</span>
                  {isActive && (
                    <motion.div
                      className="active-indicator"
                      layoutId="activeIndicator"
                      initial={false}
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    />
                  )}
                </Link>
              </motion.div>
            );
          })}
        </nav>

        <div className="header-actions">
          <motion.div
            className="stats-preview"
            whileHover={{ scale: 1.05 }}
          >
            <div className="stat-item">
              <MapPin className="stat-icon" />
              <span className="stat-value">263</span>
              <span className="stat-label">Zones</span>
            </div>
            <div className="stat-item">
              <Users className="stat-icon" />
              <span className="stat-value">10M+</span>
              <span className="stat-label">Trips</span>
            </div>
          </motion.div>

          <motion.button
            className="mobile-menu-toggle"
            onClick={toggleMobileMenu}
            whileTap={{ scale: 0.95 }}
          >
            {isMobileMenuOpen ? <X /> : <Menu />}
          </motion.button>
        </div>
      </div>

      {/* Mobile Menu */}
      <motion.nav
        className={`nav-mobile ${isMobileMenuOpen ? 'open' : ''}`}
        initial={{ opacity: 0, height: 0 }}
        animate={{ 
          opacity: isMobileMenuOpen ? 1 : 0,
          height: isMobileMenuOpen ? 'auto' : 0
        }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
      >
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <motion.div
              key={item.path}
              whileHover={{ x: 10 }}
              whileTap={{ scale: 0.95 }}
            >
              <Link
                to={item.path}
                className={`mobile-nav-link ${isActive ? 'active' : ''}`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <Icon className="mobile-nav-icon" />
                <span>{item.label}</span>
              </Link>
            </motion.div>
          );
        })}
      </motion.nav>
    </motion.header>
  );
};

export default Header;
