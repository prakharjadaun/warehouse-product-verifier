import { useEffect, useState } from 'react'
import { Button, Form, Input, Modal, Select, Table, Tag, Typography, message } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import api from '../../api/client'

const { Title } = Typography

const ROLE_COLOR = { admin: 'blue', operator: 'green' }

const columns = (onDeactivate) => [
  { title: 'Full Name', dataIndex: 'full_name', key: 'full_name' },
  { title: 'Email', dataIndex: 'email', key: 'email' },
  {
    title: 'Role', dataIndex: 'role', key: 'role',
    render: (r) => <Tag color={ROLE_COLOR[r] || 'default'}>{r?.toUpperCase()}</Tag>,
  },
  {
    title: 'Status', dataIndex: 'is_active', key: 'is_active',
    render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? 'Active' : 'Inactive'}</Tag>,
  },
]

export default function Users() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [form] = Form.useForm()
  const [messageApi, ctx] = message.useMessage()

  async function fetchUsers() {
    setLoading(true)
    try {
      const res = await api.get('/auth/users')
      setUsers(res.data)
    } catch {
      messageApi.error('Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchUsers() }, [])

  async function handleCreate(values) {
    setSubmitting(true)
    try {
      await api.post('/auth/users', values)
      messageApi.success(`User ${values.email} created`)
      setModalOpen(false)
      form.resetFields()
      fetchUsers()
    } catch (err) {
      messageApi.error(err.response?.data?.detail || 'Failed to create user')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      {ctx}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>User Management</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          Add User
        </Button>
      </div>

      <Table
        dataSource={users}
        columns={columns()}
        rowKey="id"
        loading={loading}
        size="small"
        pagination={{ pageSize: 20 }}
      />

      <Modal
        title="Create New User"
        open={modalOpen}
        onCancel={() => { setModalOpen(false); form.resetFields() }}
        footer={null}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item label="Full Name" name="full_name" rules={[{ required: true }]}>
            <Input placeholder="John Doe" />
          </Form.Item>
          <Form.Item label="Email" name="email" rules={[{ required: true, type: 'email' }]}>
            <Input placeholder="john@warehouse.com" />
          </Form.Item>
          <Form.Item label="Password" name="password" rules={[{ required: true, min: 6, message: 'Minimum 6 characters' }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item label="Role" name="role" rules={[{ required: true }]}>
            <Select options={[
              { value: 'admin', label: 'Admin — full access' },
              { value: 'operator', label: 'Operator — validate only' },
            ]} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={submitting} block>
              Create User
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
