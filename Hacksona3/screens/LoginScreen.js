import React, { useState } from 'react';
import { View, TextInput, Button, Alert } from 'react-native';
import api from '../api/client';
import AsyncStorage from '@react-native-async-storage/async-storage';

const LoginScreen = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    try {
      const response = await api.post('/login', {
        username: email,  // Ajusta según tu API (puede ser 'email' o 'username')
        password,
      });
      
      await AsyncStorage.setItem('token', response.data.access_token);
      Alert.alert('Éxito', 'Inicio de sesión correcto');
      navigation.navigate('Caudalimetros');
    } catch (error) {
      Alert.alert('Error', error.response?.data?.detail || 'Credenciales incorrectas');
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <TextInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
      />
      <TextInput
        placeholder="Contraseña"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <Button title="Iniciar sesión" onPress={handleLogin} />
    </View>
  );
};

export default LoginScreen;