import { useState } from 'react'
import { Badge, Button, Input, Table, Tag, Typography } from 'antd'
import { SearchOutlined } from '@ant-design/icons'
import api from '../../api/client'

const { Title } = Typography

const columns = [
  { title: 'WID', dataIndex: 'wid', key: 'wid', width: 130 },
  { title: 'EAN', dataIndex: 'ean', key: 'ean', width: 160 },
  { title: 'Manufacturing Date', dataIndex: 'manufacturing_date', key: 'mfg', width: 160 },
  { title: 'Expiry Date', dataIndex: 'expiry_date', key: 'exp', width: 140 },
  {
    title: 'Status', dataIndex: 'is_expired', key: 'status', width: 100,
    render: (expired) => expired
      ? <Tag color="red">Expired</Tag>
      : <Tag color="green">Valid</Tag>,
  },
]

export default function Products() {
  const [search, setSearch] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [pagination, setPagination] = useState({ current: 1, pageSize: 50, total: 0 })

  async function fetchProducts(page = 1, searchTerm = search) {
    setLoading(true)
    try {
      const res = await api.get('/products', {
        params: { search: searchTerm || undefined, page, page_size: 50 },
      })
      setData(res.data.items)
      setPagination((p) => ({ ...p, current: page, total: res.data.total }))
    } finally {
      setLoading(false)
    }
  }

  function handleSearch() {
    fetchProducts(1, search)
  }

  return (
    <div>
      <Title level={4}>Product Data</Title>

      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <Input
          placeholder="Search by WID or EAN"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onPressEnter={handleSearch}
          style={{ maxWidth: 280 }}
          allowClear
          onClear={() => { setSearch(''); fetchProducts(1, '') }}
        />
        <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch} loading={loading}>
          Search
        </Button>
        <Button onClick={() => fetchProducts(1, '')} disabled={loading}>
          Browse All
        </Button>
      </div>

      {data !== null && (
        <>
          <div style={{ marginBottom: 8, color: '#888', fontSize: 13 }}>
            {pagination.total.toLocaleString()} products found
          </div>
          <Table
            dataSource={data}
            columns={columns}
            rowKey="wid"
            loading={loading}
            size="small"
            scroll={{ x: 700 }}
            pagination={{
              ...pagination,
              showTotal: (total) => `${total.toLocaleString()} total`,
              onChange: (page) => fetchProducts(page),
            }}
            locale={{ emptyText: 'No products found' }}
          />
        </>
      )}
    </div>
  )
}
