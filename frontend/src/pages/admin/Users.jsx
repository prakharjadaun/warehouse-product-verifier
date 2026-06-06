import { Typography } from 'antd'

export default function Users() {
  return (
    <div>
      <Typography.Title level={4}>User Management</Typography.Title>
      <Typography.Text type="secondary">Available after auth/RBAC phase (Phase A3).</Typography.Text>
    </div>
  )
}
