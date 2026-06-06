import { Form, Input, Button, Card, Typography, message } from 'antd'
import { useNavigate } from 'react-router-dom'
import { jwtDecode } from 'jwt-decode'
import { useAuth } from '../context/AuthContext'
import api from '../api/client'

const { Title } = Typography

export default function Login() {
  const { login, user } = useAuth()
  const navigate = useNavigate()
  const [messageApi, contextHolder] = message.useMessage()

  if (user) {
    navigate(user.role === 'admin' ? '/admin/upload' : '/validate', { replace: true })
    return null
  }

  async function onFinish({ email, password }) {
    try {
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)
      const res = await api.post('/auth/login', formData)
      login(res.data.access_token)
      const decoded = jwtDecode(res.data.access_token)
      navigate(decoded.role === 'admin' ? '/admin/upload' : '/validate', { replace: true })
    } catch {
      messageApi.error('Invalid email or password')
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f0f2f5' }}>
      {contextHolder}
      <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        <Title level={3} style={{ textAlign: 'center', marginBottom: 24 }}>
          Warehouse Verifier
        </Title>
        <Form layout="vertical" onFinish={onFinish} autoComplete="off">
          <Form.Item label="Email" name="email" rules={[{ required: true, type: 'email', message: 'Enter a valid email' }]}>
            <Input size="large" placeholder="admin@warehouse.com" />
          </Form.Item>
          <Form.Item label="Password" name="password" rules={[{ required: true, message: 'Password is required' }]}>
            <Input.Password size="large" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" size="large" block>
              Login
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}
