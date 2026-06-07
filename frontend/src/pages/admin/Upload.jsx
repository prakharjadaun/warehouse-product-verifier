import { useEffect, useRef, useState } from 'react'
import { Alert, Badge, Progress, Statistic, Table, Tag, Typography, Upload, notification } from 'antd'
import { InboxOutlined } from '@ant-design/icons'
import api from '../../api/client'

const { Title, Text } = Typography
const { Dragger } = Upload

const STATUS_COLOR = { pending: 'default', processing: 'processing', completed: 'success', failed: 'error' }

const historyColumns = [
  { title: 'Filename', dataIndex: 'filename', key: 'filename', ellipsis: true },
  {
    title: 'Status', dataIndex: 'status', key: 'status',
    render: (s) => <Badge status={STATUS_COLOR[s] || 'default'} text={s} />,
  },
  {
    title: 'Progress', key: 'progress',
    render: (_, r) => (
      <Progress
        percent={r.progress_percent}
        size="small"
        status={r.status === 'failed' ? 'exception' : r.status === 'completed' ? 'success' : 'active'}
        style={{ minWidth: 120 }}
      />
    ),
  },
  {
    title: 'Rows', key: 'rows',
    render: (_, r) => r.total_rows
      ? `${(r.processed_rows || 0).toLocaleString()} / ${r.total_rows.toLocaleString()}`
      : '—',
  },
  {
    title: 'Uploaded', dataIndex: 'created_at', key: 'created_at',
    render: (v) => v ? new Date(v).toLocaleString() : '—',
  },
]

export default function UploadPage() {
  const [jobId, setJobId] = useState(null)
  const [jobStatus, setJobStatus] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const pollRef = useRef(null)

  async function loadHistory() {
    try {
      const res = await api.get('/uploads?limit=10')
      setHistory(res.data)
    } catch { /* silent */ }
  }

  useEffect(() => {
    loadHistory()
  }, [])

  function stopPolling() {
    if (pollRef.current) clearInterval(pollRef.current)
  }

  function startPolling(id) {
    pollRef.current = setInterval(async () => {
      try {
        const res = await api.get(`/uploads/${id}/status`)
        setJobStatus(res.data)
        // Also refresh history so table stays live
        loadHistory()
        if (res.data.status === 'completed') {
          stopPolling()
          setUploading(false)
          notification.success({
            message: 'Upload complete',
            description: `${(res.data.processed_rows || 0).toLocaleString()} rows ingested successfully`,
          })
        } else if (res.data.status === 'failed') {
          stopPolling()
          setUploading(false)
          notification.error({ message: 'Upload failed', description: res.data.error_message })
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
      loadHistory()
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed')
      setUploading(false)
    }
  }

  const percent = jobStatus?.progress_percent ?? 0
  const isComplete = jobStatus?.status === 'completed'
  const isFailed = jobStatus?.status === 'failed'

  return (
    <div>
      <Title level={4}>Upload Product Data</Title>

      <Dragger
        accept=".csv"
        beforeUpload={(file) => {
          if (!file.name.endsWith('.csv')) {
            setError('Only CSV files are accepted')
            return Upload.LIST_IGNORE
          }
          return true
        }}
        customRequest={handleUpload}
        showUploadList={false}
        disabled={uploading}
        style={{ marginBottom: 24 }}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined style={{ fontSize: 48, color: '#1677ff' }} />
        </p>
        <p style={{ fontSize: 16 }}>Click or drag CSV file here to upload</p>
        <p style={{ color: '#888', fontSize: 12 }}>Columns: WID, EAN, Manufacturing_Date, Expiry_Date</p>
      </Dragger>

      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} showIcon />}

      {jobId && (
        <div style={{ marginBottom: 24 }}>
          <Text type="secondary" style={{ fontSize: 12 }}>Job ID: {jobId}</Text>
          <Progress
            percent={percent}
            status={isFailed ? 'exception' : isComplete ? 'success' : 'active'}
            style={{ marginTop: 8, marginBottom: 12 }}
          />
          <div style={{ display: 'flex', gap: 32 }}>
            <Statistic title="Processed" value={jobStatus?.processed_rows ?? 0} formatter={(v) => v.toLocaleString()} />
            <Statistic title="Total Rows" value={jobStatus?.total_rows ?? '—'} formatter={(v) => typeof v === 'number' ? v.toLocaleString() : v} />
            <Statistic title="Status" value={jobStatus?.status ?? 'pending'} />
          </div>
        </div>
      )}

      <Title level={5} style={{ marginTop: 8 }}>Upload History</Title>
      <Table
        dataSource={history}
        columns={historyColumns}
        rowKey="job_id"
        size="small"
        pagination={false}
        locale={{ emptyText: 'No uploads yet' }}
      />
    </div>
  )
}
