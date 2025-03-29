import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, Button } from 'react-native';
import api from '../api/client';

const CaudalimetrosScreen = () => {
  const [caudalimetros, setCaudalimetros] = useState([]);

  const fetchCaudalimetros = async () => {
    try {
      const response = await api.get('/caudalimetros');
      setCaudalimetros(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchCaudalimetros();
  }, []);

  return (
    <View style={{ padding: 20 }}>
      <FlatList
        data={caudalimetros}
        keyExtractor={(item) => item._id}
        renderItem={({ item }) => (
          <View style={{ marginBottom: 10 }}>
            <Text>Nombre: {item.nombre}</Text>
            <Text>Tipo: {item.tipo}</Text>
            <Text>Consumo total: {item.mediciones.reduce((acc, m) => acc + m.consumo_total, 0)} L</Text>
          </View>
        )}
      />
      <Button
        title="Obtener recomendaciones"
        onPress={async () => {
          try {
            const response = await api.post('/analisis', { user_id: 'tu_user_id' });
            console.log(response.data);
          } catch (error) {
            console.error(error);
          }
        }}
      />
    </View>
  );
};

export default CaudalimetrosScreen;