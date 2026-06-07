import { useRef, useState } from 'react'
import {
  Alert, Badge, Button, Card, Descriptions, Divider, Input,
  Space, Spin, Tag, Typography, Upload, message,
} from 'antd'
import { CameraOutlined, SearchOutlined, UploadOutlined } from '@ant-design/icons'
import { useAuth } from '../../context/AuthContext'
import api from '../../api/client'

const { Title, Text } = Typography
const { Dragger } = Upload

export default function Verify() {
  const { user } = useAuth()
  const [wid, setWid] = useState('')
  const [product, setProduct] = useState(null)
  const [productLoading, setProductLoading] = useState(false)
  const [productError, setProductError] = useState(null)

  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [aiResult, setAiResult] = useState(null)
  const [messageApi, ctx] = message.useMessage()
  const cameraRef = useRef()

  async function lookupWID() {
    const trimmed = wid.trim()
    if (!trimmed) return
    setProductLoading(true)
    setProductError(null)
    setProduct(null)
    setAiResult(null)
    setImageFile(null)
    setImagePreview(null)
    try {
      const res = await api.get(`/products/${trimmed}`)
      setProduct(res.data)
    } catch (err) {
      setProductError(err.response?.status === 404 ? `WID ${trimmed} not found` : 'Lookup failed')
    } finally {
      setProductLoading(false)
    }
  }

  function handleImageSelect(file) {
    setImageFile(file)
    setImagePreview(URL.createObjectURL(file))
    setAiResult(null)
    return false // prevent antd auto-upload
  }

  async function runAIVerification() {
    if (!imageFile || !product) return
    setAiLoading(true)
    setAiResult(null)
    try {
      const formData = new FormData()
      formData.append('wid', product.wid)
      formData.append('operator_id', user?.sub || 'admin')
      formData.append('image', imageFile)
      const res = await api.post('/verifications/ai-extract', formData)
      setAiResult(res.data)
      messageApi.success('AI verification complete — result saved to database')
    } catch (err) {
      messageApi.error('AI extraction failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setAiLoading(false)
    }
  }

  const matchStatus = aiResult?.ai_match_status
  const alertType = matchStatus === 'match' ? 'success' : matchStatus === 'mismatch' ? 'error' : 'warning'

  return (
    <div style={{ maxWidth: 680 }}>
      {ctx}
      <Title level={4}>Product Verification</Title>
      <Text type="secondary">
        Look up a product by WID, upload or capture its label image, and let AI extract and validate the dates.
      </Text>

      <Divider />

      {/* Step 1 — WID lookup */}
      <Text strong>Step 1 — Enter WID</Text>
      <Space.Compact style={{ width: '100%', marginTop: 8, marginBottom: 16 }}>
        <Input
          size="large"
          placeholder="Enter Warehouse ID (WID)"
          value={wid}
          onChange={(e) => setWid(e.target.value)}
          onPressEnter={lookupWID}
        />
        <Button size="large" type="primary" icon={<SearchOutlined />} onClick={lookupWID} loading={productLoading}>
          Lookup
        </Button>
      </Space.Compact>

      {productError && <Alert type="error" message={productError} showIcon style={{ marginBottom: 16 }} />}

      {product && (
        <Card style={{ marginBottom: 20 }}>
          <Descriptions title="Product Details" column={2} size="small" bordered>
            <Descriptions.Item label="WID">{product.wid}</Descriptions.Item>
            <Descriptions.Item label="EAN">{product.ean}</Descriptions.Item>
            <Descriptions.Item label="Manufacturing Date">{product.manufacturing_date}</Descriptions.Item>
            <Descriptions.Item label="Expiry Date">
              {product.expiry_date}{' '}
              {product.is_expired
                ? <Tag color="red">EXPIRED</Tag>
                : <Tag color="green">Valid</Tag>}
            </Descriptions.Item>
          </Descriptions>
        </Card>
      )}

      {/* Step 2 — Image upload */}
      {product && (
        <>
          <Text strong>Step 2 — Upload or Capture Product Label Image</Text>
          <div style={{ marginTop: 8, marginBottom: 16 }}>
            <Dragger
              accept="image/*"
              beforeUpload={handleImageSelect}
              showUploadList={false}
              style={{ marginBottom: 8 }}
            >
              <p className="ant-upload-drag-icon">
                <UploadOutlined style={{ fontSize: 32, color: '#1677ff' }} />
              </p>
              <p>Click or drag image file here</p>
            </Dragger>

            {/* Camera capture for mobile */}
            <Button
              icon={<CameraOutlined />}
              onClick={() => cameraRef.current.click()}
              style={{ width: '100%' }}
            >
              Use Camera (Mobile)
            </Button>
            <input
              ref={cameraRef}
              type="file"
              accept="image/*"
              capture="environment"
              style={{ display: 'none' }}
              onChange={(e) => e.target.files[0] && handleImageSelect(e.target.files[0])}
            />
          </div>

          {imagePreview && (
            <div style={{ marginBottom: 16 }}>
              <Text type="secondary" style={{ display: 'block', marginBottom: 6 }}>Selected image:</Text>
              <img
                src={imagePreview}
                alt="product label"
                style={{ maxWidth: '100%', maxHeight: 280, borderRadius: 6, border: '1px solid #d9d9d9' }}
              />
            </div>
          )}

          {/* Step 3 — Run AI */}
          {imageFile && (
            <>
              <Text strong>Step 3 — Run AI Extraction</Text>
              <div style={{ marginTop: 8, marginBottom: 16 }}>
                <Button
                  type="primary"
                  size="large"
                  onClick={runAIVerification}
                  loading={aiLoading}
                  style={{ width: '100%' }}
                >
                  {aiLoading ? 'Extracting dates with GPT-4o...' : 'Run AI Verification'}
                </Button>
              </div>
            </>
          )}

          {/* AI Result */}
          {aiResult && (
            <Card
              style={{ borderColor: matchStatus === 'match' ? '#52c41a' : matchStatus === 'mismatch' ? '#ff4d4f' : '#faad14' }}
            >
              <Alert
                type={alertType}
                message={`AI Result: ${matchStatus?.toUpperCase()}`}
                showIcon
                style={{ marginBottom: 12 }}
              />
              <Descriptions column={2} size="small" bordered>
                <Descriptions.Item label="AI — Mfg Date">
                  {aiResult.ai_mfg_date || '—'}
                </Descriptions.Item>
                <Descriptions.Item label="DB — Mfg Date">
                  {aiResult.db_mfg_date || '—'}
                </Descriptions.Item>
                <Descriptions.Item label="AI — Expiry Date">
                  {aiResult.ai_expiry_date || '—'}
                </Descriptions.Item>
                <Descriptions.Item label="DB — Expiry Date">
                  {aiResult.db_expiry_date || '—'}
                </Descriptions.Item>
              </Descriptions>
              <Text type="secondary" style={{ fontSize: 12, marginTop: 8, display: 'block' }}>
                Verification ID: {aiResult.id} — saved to database
              </Text>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
