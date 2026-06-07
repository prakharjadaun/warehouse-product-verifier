import { Layout, Menu } from 'antd'
import { UploadOutlined, BarChartOutlined, TeamOutlined, DatabaseOutlined, LogoutOutlined } from '@ant-design/icons'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const { Sider, Content } = Layout

const menuItems = [
  { key: '/admin/upload', icon: <UploadOutlined />, label: 'Upload CSV' },
  { key: '/admin/products', icon: <DatabaseOutlined />, label: 'Products' },
  { key: '/admin/reports', icon: <BarChartOutlined />, label: 'Reports' },
  { key: '/admin/users', icon: <TeamOutlined />, label: 'Users' },
  { key: 'logout', icon: <LogoutOutlined />, label: 'Logout', danger: true },
]

export default function AdminLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { logout } = useAuth()

  function onMenuClick({ key }) {
    if (key === 'logout') { logout(); navigate('/login'); return }
    navigate(key)
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="light" collapsible breakpoint="lg">
        <div style={{ padding: '16px 20px', fontWeight: 700, fontSize: 15, color: '#1677ff', borderBottom: '1px solid #f0f0f0' }}>
          WMS Admin
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={onMenuClick}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <Content style={{ margin: 24, padding: 24, background: '#fff', borderRadius: 8, minHeight: 280 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
