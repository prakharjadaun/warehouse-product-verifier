import { useRef, useState } from 'react'
import { Alert, Progress, Statistic, Typography, Upload, notification } from 'antd'
import { InboxOutlined } from '@ant-design/icons'
import api from '../../api/client'

const { Title, Text } = Typography
const { Dragger } = Upload

export default function UploadPage() {
  const [jobId, setJobId] = useState(null)
  const [jobStatus, setJobStatus] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const pollRef = useRef(null)

  function stopPolling() {
    if (pollRef.current) clearInterval(pollRef.current)
  }

  function startPolling(id) {
    pollRef.current = setInterval(async () => {
      try {
        const res = await api.get(`/uploads/${id}/status`)
        setJobStatus(res.data)
        if (res.data.status === 'completed') {
          stopPolling()
          setUploading(false)
          notification.success({ message: 'Upload complete', description: `${res.data.processed_rows.toLocaleString()} rows ingested` })
        } else if (res.data.status === 'failed') {
          stopPolling()
          setUploading(false)
        }
      } catch {
        stopPolling()
        setUploading(false)
      }
    }, 2000)
  }

  async function handleUpload({ file }) {
    setError(null)
    setJobId(null)
    setJobStatus(null)
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await api.post('/uploads/csv', formData)
      const id = res.data.job_id
      setJobId(id)
      startPolling(id)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed')
      setUploading(false)
    }
    return false
  }

  const percent = jobStatus?.progress_percent ?? 0
  const isComplete = jobStatus?.status === 'completed'
  const isFailed = jobStatus?.status === 'failed'

  return (
    <div>
      <Title level={4}>Upload Product Data</Title>

      <Dragger
        accept=".csv"
        beforeUpload={() => false}
        customRequest={handleUpload}
        showUploadList={false}
        disabled={uploading}
        style={{ marginBottom: 24 }}
      >
        <p className="ant-upload-drag-icon"><InboxOutlined style={{ fontSize: 48, color: '#1677ff' }} /></p>
        <p style={{ fontSize: 16 }}>Click or drag CSV file here to upload</p>
        <p style={{ color: '#888', fontSize: 12 }}>Columns: WID, EAN, Manufacturing_Date, Expiry_Date</p>
      </Dragger>

      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} showIcon />}

      {jobId && (
        <div style={{ marginTop: 16 }}>
          <Text type="secondary" style={{ fontSize: 12 }}>Job ID: {jobId}</Text>
          <Progress
            percent={percent}
            status={isFailed ? 'exception' : isComplete ? 'success' : 'active'}
            style={{ marginTop: 8, marginBottom: 12 }}
          />
          <div style={{ display: 'flex', gap: 32 }}>
            <Statistic title="Processed Rows" value={jobStatus?.processed_rows ?? 0} formatter={(v) => v.toLocaleString()} />
            <Statistic title="Total Rows" value={jobStatus?.total_rows ?? '—'} formatter={(v) => typeof v === 'number' ? v.toLocaleString() : v} />
            <Statistic title="Status" value={jobStatus?.status ?? 'pending'} />
          </div>
          {isFailed && <Alert type="error" message={`Error: ${jobStatus?.error_message}`} style={{ marginTop: 12 }} showIcon />}
        </div>
      )}
    </div>
  )
}
