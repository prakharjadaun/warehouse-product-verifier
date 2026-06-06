import { useState } from 'react'
import { Button, DatePicker, Space, Table, Tag, Typography } from 'antd'
import { DownloadOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import api from '../../api/client'

const { Title } = Typography
const { RangePicker } = DatePicker

const STATUS_COLOR = { match: 'green', mismatch: 'red', skipped: 'default', error: 'orange' }

const columns = [
  { title: 'WID', dataIndex: 'wid', key: 'wid', width: 120 },
  { title: 'Operator', dataIndex: 'operator_id', key: 'operator_id', render: (v) => v || '—' },
  { title: 'Verified At', dataIndex: 'verified_at', key: 'verified_at', render: (v) => new Date(v).toLocaleString() },
  { title: 'DB Mfg Date', dataIndex: 'db_mfg_date', key: 'db_mfg_date', render: (v) => v || '—' },
  { title: 'DB Expiry', dataIndex: 'db_expiry_date', key: 'db_expiry_date', render: (v) => v || '—' },
  {
    title: 'AI Status', dataIndex: 'ai_match_status', key: 'ai_match_status',
    render: (v) => <Tag color={STATUS_COLOR[v] || 'default'}>{v?.toUpperCase()}</Tag>,
  },
]

export default function Reports() {
  const [dates, setDates] = useState(null)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [pagination, setPagination] = useState({ current: 1, pageSize: 50, total: 0 })

  async function fetchReport(page = 1) {
    if (!dates) return
    setLoading(true)
    try {
      const [start, end] = dates
      const res = await api.get('/reports/verifications', {
        params: {
          start_date: start.format('YYYY-MM-DD'),
          end_date: end.format('YYYY-MM-DD'),
          page,
          page_size: 50,
        },
      })
      setData(res.data.items)
      setPagination((p) => ({ ...p, current: page, total: res.data.total }))
    } finally {
      setLoading(false)
    }
  }

  function handleDownload() {
    if (!data) return
    const headers = ['wid', 'operator_id', 'verified_at', 'db_mfg_date', 'db_expiry_date', 'ai_match_status']
    const csv = [headers.join(','), ...data.map((r) => headers.map((h) => r[h] ?? '').join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `report_${dayjs().format('YYYY-MM-DD')}.csv`; a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div>
      <Title level={4}>Verification Reports</Title>
      <Space style={{ marginBottom: 16 }} wrap>
        <RangePicker onChange={setDates} />
        <Button type="primary" onClick={() => fetchReport(1)} disabled={!dates} loading={loading}>
          Generate Report
        </Button>
        {data && (
          <Button icon={<DownloadOutlined />} onClick={handleDownload}>
            Download CSV
          </Button>
        )}
      </Space>

      {data !== null && (
        <Table
          dataSource={data}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            showTotal: (total) => `${total} records`,
            onChange: (page) => fetchReport(page),
          }}
          size="small"
          scroll={{ x: 800 }}
          locale={{ emptyText: 'No verification records in this date range' }}
        />
      )}
    </div>
  )
}
