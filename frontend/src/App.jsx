import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import PrivateRoute from './components/PrivateRoute'
import Login from './pages/Login'
import AdminLayout from './pages/admin/AdminLayout'
import Upload from './pages/admin/Upload'
import Products from './pages/admin/Products'
import Reports from './pages/admin/Reports'
import Users from './pages/admin/Users'
import Validate from './pages/operator/Validate'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            path="/admin"
            element={
              <PrivateRoute requiredRole="admin">
                <AdminLayout />
              </PrivateRoute>
            }
          >
            <Route index element={<Navigate to="upload" replace />} />
            <Route path="upload" element={<Upload />} />
            <Route path="products" element={<Products />} />
            <Route path="reports" element={<Reports />} />
            <Route path="users" element={<Users />} />
          </Route>

          <Route
            path="/validate"
            element={
              <PrivateRoute>
                <Validate />
              </PrivateRoute>
            }
          />

          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
