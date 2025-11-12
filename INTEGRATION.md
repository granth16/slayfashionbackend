# 📱 Frontend Integration Guide

How to integrate this backend with your React Native app.

## 1. Update Backend URL

In your React Native app, update the backend URL:

```typescript
// src/config/backend.ts or wherever you store config
export const BACKEND_CONFIG = {
  // Development
  apiUrl: __DEV__ 
    ? Platform.OS === 'android'
      ? 'http://10.0.2.2:8000'  // Android emulator
      : 'http://localhost:8000'  // iOS simulator
    : 'https://your-production-api.com',  // Production
};
```

For **physical devices**, use your computer's IP address:
```typescript
apiUrl: 'http://192.168.1.100:8000'  // Replace with your IP
```

## 2. Create Authentication Service

Create a new service file:

```typescript
// src/services/authService.ts
import axios from 'axios';
import { BACKEND_CONFIG } from '../config/backend';

const api = axios.create({
  baseURL: BACKEND_CONFIG.apiUrl,
  timeout: 15000,
});

export interface SendOTPResponse {
  success: boolean;
  message: string;
  session_id?: string;
}

export interface VerifyOTPResponse {
  success: boolean;
  message: string;
  customer?: {
    id: string;
    phone: string;
    email: string;
    first_name: string;
    last_name: string;
    shopify_customer_id: string;
  };
  access_token?: string;
  token_expires_at?: string;
}

/**
 * Send OTP to phone number
 */
export async function sendOTP(phone: string): Promise<SendOTPResponse> {
  try {
    const response = await api.post('/api/auth/send-otp', { phone });
    return response.data;
  } catch (error: any) {
    console.error('Send OTP error:', error);
    throw new Error(
      error.response?.data?.detail || 'Failed to send OTP'
    );
  }
}

/**
 * Verify OTP and login
 */
export async function verifyOTP(
  phone: string,
  otp: string,
  sessionId: string
): Promise<VerifyOTPResponse> {
  try {
    const response = await api.post('/api/auth/verify-otp', {
      phone,
      otp,
      session_id: sessionId,
    });
    return response.data;
  } catch (error: any) {
    console.error('Verify OTP error:', error);
    throw new Error(
      error.response?.data?.detail || 'Failed to verify OTP'
    );
  }
}
```

## 3. Update Login Screen

Replace your existing login logic:

```typescript
// src/screens/LoginScreen.tsx
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert } from 'react-native';
import { sendOTP, verifyOTP } from '../services/authService';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function LoginScreen({ navigation }) {
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const [loading, setLoading] = useState(false);

  const handleSendOTP = async () => {
    if (!phone || phone.length < 10) {
      Alert.alert('Error', 'Please enter a valid phone number');
      return;
    }

    setLoading(true);
    try {
      // Add country code if not present
      const formattedPhone = phone.startsWith('+') ? phone : `+91${phone}`;
      
      const response = await sendOTP(formattedPhone);
      
      if (response.success && response.session_id) {
        setSessionId(response.session_id);
        setStep('otp');
        Alert.alert('Success', 'OTP sent to your phone!');
      } else {
        Alert.alert('Error', response.message);
      }
    } catch (error: any) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    if (!otp || otp.length !== 6) {
      Alert.alert('Error', 'Please enter a valid 6-digit OTP');
      return;
    }

    setLoading(true);
    try {
      const formattedPhone = phone.startsWith('+') ? phone : `+91${phone}`;
      
      const response = await verifyOTP(formattedPhone, otp, sessionId);
      
      if (response.success && response.access_token && response.customer) {
        // Store customer data and access token
        await AsyncStorage.setItem('customer_data', JSON.stringify(response.customer));
        await AsyncStorage.setItem('shopify_access_token', response.access_token);
        await AsyncStorage.setItem('token_expires_at', response.token_expires_at || '');
        
        Alert.alert('Success', `Welcome ${response.customer.first_name || 'back'}!`);
        
        // Navigate to home or orders screen
        navigation.replace('Home');
      } else {
        Alert.alert('Error', response.message);
      }
    } catch (error: any) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ padding: 20 }}>
      {step === 'phone' ? (
        <>
          <Text style={{ fontSize: 24, marginBottom: 20 }}>Login with Phone</Text>
          
          <TextInput
            placeholder="Phone Number (e.g., 9876543210)"
            value={phone}
            onChangeText={setPhone}
            keyboardType="phone-pad"
            style={{
              borderWidth: 1,
              borderColor: '#ccc',
              padding: 15,
              borderRadius: 8,
              marginBottom: 20,
            }}
          />
          
          <TouchableOpacity
            onPress={handleSendOTP}
            disabled={loading}
            style={{
              backgroundColor: '#000',
              padding: 15,
              borderRadius: 8,
              alignItems: 'center',
            }}
          >
            <Text style={{ color: '#fff', fontWeight: 'bold' }}>
              {loading ? 'Sending...' : 'Send OTP'}
            </Text>
          </TouchableOpacity>
        </>
      ) : (
        <>
          <Text style={{ fontSize: 24, marginBottom: 10 }}>Enter OTP</Text>
          <Text style={{ color: '#666', marginBottom: 20 }}>
            Sent to {phone}
          </Text>
          
          <TextInput
            placeholder="6-digit OTP"
            value={otp}
            onChangeText={setOtp}
            keyboardType="number-pad"
            maxLength={6}
            style={{
              borderWidth: 1,
              borderColor: '#ccc',
              padding: 15,
              borderRadius: 8,
              marginBottom: 20,
              fontSize: 24,
              letterSpacing: 10,
              textAlign: 'center',
            }}
          />
          
          <TouchableOpacity
            onPress={handleVerifyOTP}
            disabled={loading}
            style={{
              backgroundColor: '#000',
              padding: 15,
              borderRadius: 8,
              alignItems: 'center',
              marginBottom: 10,
            }}
          >
            <Text style={{ color: '#fff', fontWeight: 'bold' }}>
              {loading ? 'Verifying...' : 'Verify & Login'}
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            onPress={() => setStep('phone')}
            style={{ alignItems: 'center', padding: 10 }}
          >
            <Text style={{ color: '#666' }}>Change Phone Number</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
}
```

## 4. Fetch Customer Orders

Now that you have the `access_token`, you can use it with Shopify Storefront API:

```typescript
// src/services/shopifyStorefront.ts
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SHOPIFY_CONFIG } from '../config/shopify';

const storefrontAPI = axios.create({
  baseURL: `https://${SHOPIFY_CONFIG.storeDomain}/api/${SHOPIFY_CONFIG.apiVersion}/graphql.json`,
  headers: {
    'Content-Type': 'application/json',
    'X-Shopify-Storefront-Access-Token': SHOPIFY_CONFIG.storefrontAccessToken,
  },
});

/**
 * Fetch customer orders using access token
 */
export async function fetchCustomerOrders() {
  const accessToken = await AsyncStorage.getItem('shopify_access_token');
  
  if (!accessToken) {
    throw new Error('Not logged in');
  }

  const query = `
    query($customerAccessToken: String!) {
      customer(customerAccessToken: $customerAccessToken) {
        id
        firstName
        lastName
        email
        phone
        orders(first: 50, sortKey: PROCESSED_AT, reverse: true) {
          edges {
            node {
              id
              orderNumber
              name
              processedAt
              totalPriceV2 {
                amount
                currencyCode
              }
              financialStatus
              fulfillmentStatus
              lineItems(first: 10) {
                edges {
                  node {
                    title
                    quantity
                    variant {
                      id
                      title
                      priceV2 {
                        amount
                      }
                      image {
                        url
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  `;

  const response = await storefrontAPI.post('', {
    query,
    variables: { customerAccessToken: accessToken },
  });

  const customer = response.data.data.customer;
  
  if (!customer) {
    throw new Error('Invalid access token');
  }

  const orders = customer.orders.edges.map((edge: any) => edge.node);
  
  return { customer, orders };
}
```

## 5. Test the Integration

### Development Testing

1. **Start Backend**:
   ```bash
   cd slayfashionbackend
   python run.py
   ```

2. **Start React Native**:
   ```bash
   cd ../SLAYFASHIONAPP/SlayFashionApp
   npm start
   ```

3. **Test Flow**:
   - Open app
   - Enter phone number
   - Check backend console for OTP (in dev mode)
   - Enter OTP
   - Should see success and navigate to home

### Common Issues

**❌ "Network Error" / "Cannot connect"**

Solution: Check your backend URL
- Android emulator: Use `http://10.0.2.2:8000`
- iOS simulator: Use `http://localhost:8000`
- Physical device: Use your computer's IP (e.g., `http://192.168.1.100:8000`)

**❌ "Invalid OTP"**

Solution: 
- Check backend console for actual OTP code
- Make sure session_id is correct
- Check if OTP expired (10 minutes)

**❌ Backend responds but returns 500 error**

Solution:
- Check Shopify credentials in `.env`
- Make sure Admin API and Storefront API tokens are valid
- Check backend logs for detailed error

## 6. Deploy to Production

When ready for production:

1. **Deploy Backend** (see README.md for deployment guides)
2. **Update Frontend Config**:
   ```typescript
   apiUrl: 'https://your-api.railway.app'
   ```
3. **Enable Real SMS**:
   - Set up Twilio account
   - Add real credentials to backend `.env`

---

You're all set! 🎉

Your app now has:
✅ OTP-based login
✅ Automatic Shopify customer creation
✅ Seamless token-based authentication
✅ No password required for users

Just like GoKwik/KwikPass! 🚀

