import React, { createContext, useState, useEffect } from 'react';
import API from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      API.get('/auth/me')
        .then((res) => {
          setUser(res.data);
        })
        .catch(() => {
          logout();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const res = await API.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    const { access_token, refresh_token } = res.data;
    localStorage.setItem('token', access_token);
    if (refresh_token) {
      localStorage.setItem('refreshToken', refresh_token);
    }
    setToken(access_token);

    const userRes = await API.get('/auth/me', {
      headers: { Authorization: `Bearer ${access_token}` }
    });
    setUser(userRes.data);
    return userRes.data;
  };

  const register = async (email, password, fullName, role = 'user') => {
    const res = await API.post('/auth/register', {
      email,
      password,
      full_name: fullName,
      role
    });

    const { access_token, refresh_token } = res.data;
    if (access_token) {
      localStorage.setItem('token', access_token);
      if (refresh_token) {
        localStorage.setItem('refreshToken', refresh_token);
      }
      setToken(access_token);
      const userRes = await API.get('/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      setUser(userRes.data);
    }
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
