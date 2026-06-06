import { useState } from 'react'
import { Alert, Badge, Button, Card, Descriptions, Input, Space, Typography } from 'antd'
import { LogoutOutlined, SearchOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import api from '../../api/client'

const { Title } = Typography

export default function Validate() {
  const [wid, setWid] = useState('')
  const [product, setProduct] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [aiResult, setAiResult] = useState(null)
  const [aiLoading, setAiLoading] = useState(false)
  const { logout, user } = useAuth()
  const navigate = useNavigate()

  async function lookupProduct() {
    const trimmed = wid.trim()
    if (!trimmed) return
    setLoading(true)
    setError(null)
    setProduct(null)
    setAiResult(null)
    try {
      const res = await api.get(`/products/${trimmed}`)
      setProduct(res.data)
      await api.post('/verifications', { wid: parseInt(trimmed), operator_id: user?.sub || null })
    } catch (err) {
      setError(err.response?.status === 404 ? `WID ${trimmed} not found in system` : 'Lookup failed')
    } finally {
      setLoading(false)
    }
  }

  async function handleImageCapture(e) {
    const file = e.target.files[0]
    if (!file || !product) return
    setAiLoading(true)
    setAiResult(null)
    try {
      const formData = new FormData()
      formData.append('wid', product.wid)
      formData.append('operator_id', user?.sub || '')
      formData.append('image', file)
      const res = await api.post('/verifications/ai-extract', formData)
      setAiResult(res.data)
    } catch {
      setAiResult({ ai_match_status: 'error' })
    } finally {
      setAiLoading(false)
    }
  }

  function handleLogout() { logout(); navigate('/login') }

  return (
    <div style={{ maxWidth: 500, margin: '40px auto', padding: '0 16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={4} style={{ margin: 0 }}>Product Verification</Title>
        <Button icon={<LogoutOutlined />} onClick={handleLogout} type="text" />
      </div>

      <Space.Compact style={{ width: '100%', marginBottom: 16 }}>
        <Input
          size="large"
          placeholder="Enter or scan WID"
          value={wid}
          onChange={(e) => setWid(e.target.value)}
          onPressEnter={lookupProduct}
          style={{ fontSize: 18 }}
          autoFocus
        />
        <Button size="large" type="primary" icon={<SearchOutlined />} onClick={lookupProduct} loading={loading}>
          Lookup
        </Button>
      </Space.Compact>

      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}

      {product && (
        <>
          <Card style={{ marginBottom: 16 }}>
            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="WID">{product.wid}</Descriptions.Item>
              <Descriptions.Item label="EAN">{product.ean}</Descriptions.Item>
              <Descriptions.Item label="Manufactured">{product.manufacturing_date}</Descriptions.Item>
              <Descriptions.Item label="Expires">
                <span style={{ marginRight: 8 }}>{product.expiry_date}</span>
                {product.is_expired
                  ? <Badge status="error" text="EXPIRED" />
                  : <Badge status="success" text="Valid" />}
              </Descriptions.Item>
            </Descriptions>
          </Card>

          <Button
            size="large"
            style={{ width: '100%', marginBottom: 12 }}
            loading={aiLoading}
            onClick={() => document.getElementById('camera-input').click()}
          >
            📷 Capture Label &amp; AI Verify
          </Button>
          <input
            id="camera-input"
            type="file"
            accept="image/*"
            capture="environment"
            style={{ display: 'none' }}
            onChange={handleImageCapture}
          />

          {aiResult && (
            <Alert
              type={
                aiResult.ai_match_status === 'match' ? 'success'
                  : aiResult.ai_match_status === 'mismatch' ? 'error'
                    : 'warning'
              }
              message={`AI Verification: ${aiResult.ai_match_status?.toUpperCase()}`}
              description={
                aiResult.ai_mfg_date
                  ? `Extracted — Mfg: ${aiResult.ai_mfg_date} | Exp: ${aiResult.ai_expiry_date}`
                  : 'Could not extract dates from image'
              }
              showIcon
            />
          )}
        </>
      )}
    </div>
  )
}
