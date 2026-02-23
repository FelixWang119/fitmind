import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Heart, Mail, Lock, User, Scale } from 'lucide-react'
import toast from 'react-hot-toast'

const Auth: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirm_password: '',
    username: '',
    full_name: '',
    age: '',
    gender: '',
    height: '',
    initial_weight: '',
    target_weight: '',
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(false)
  
  const navigate = useNavigate()
  const { login, register, error, clearError } = useAuthStore()

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    
    // 邮箱验证
    if (!formData.email) {
      newErrors.email = '邮箱不能为空'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '邮箱格式不正确'
    }
    
    // 密码验证
    if (!formData.password) {
      newErrors.password = '密码不能为空'
    } else if (formData.password.length < 8) {
      newErrors.password = '密码至少需要8个字符'
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = '密码必须包含大小写字母和数字'
    }
    
    // 确认密码验证
    if (!isLogin) {
      if (!formData.confirm_password) {
        newErrors.confirm_password = '请确认密码'
      } else if (formData.password !== formData.confirm_password) {
        newErrors.confirm_password = '两次输入的密码不一致'
      }
    }
    
    // 用户名验证
    if (!isLogin && !formData.username) {
      newErrors.username = '用户名不能为空'
    } else if (!isLogin && formData.username.length < 3) {
      newErrors.username = '用户名至少需要3个字符'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // 表单验证
    if (!validateForm()) {
      toast.error('请检查表单错误')
      return
    }
    
    setIsLoading(true)
    clearError()

    try {
      if (isLogin) {
        await login(formData.email, formData.password)
        toast.success('登录成功！')
        navigate('/')
      } else {
        const userData = {
          email: formData.email,
          password: formData.password,
          confirm_password: formData.confirm_password,
          username: formData.username,
          full_name: formData.full_name || undefined,
          age: formData.age ? parseInt(formData.age) : undefined,
          gender: formData.gender || undefined,
          height: formData.height ? parseInt(formData.height) : undefined,
          initial_weight: formData.initial_weight ? parseInt(formData.initial_weight) * 1000 : undefined,
          target_weight: formData.target_weight ? parseInt(formData.target_weight) * 1000 : undefined,
        }
        await register(userData)
        toast.success('注册成功！请登录')
        setIsLogin(true)
        setFormData(prev => ({ 
          ...prev, 
          password: '',
          confirm_password: ''
        }))
      }
    } catch (err: any) {
      // 处理API错误
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail
        if (typeof detail === 'object' && detail.message) {
          const errorMessage = detail.message
          toast.error(errorMessage)
          
          // 如果是"邮箱未注册"错误，显示注册提示
          if (errorMessage.includes('邮箱未注册') && isLogin) {
            // 可以在这里添加一个提示，引导用户去注册
            setTimeout(() => {
              toast((t) => (
                <div className="flex flex-col space-y-2">
                  <span>还没有账号？</span>
                  <button
                    onClick={() => {
                      setIsLogin(false)
                      toast.dismiss(t.id)
                    }}
                    className="text-primary-600 hover:text-primary-700 font-medium underline"
                  >
                    立即注册
                  </button>
                </div>
              ), { duration: 5000 })
            }, 100)
          }
        } else if (typeof detail === 'string') {
          toast.error(detail)
        } else {
          toast.error('操作失败')
        }
      } else {
        toast.error(error || '操作失败')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    
    // 清除该字段的错误
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[name]
        return newErrors
      })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
        {/* 头部 */}
        <div className="bg-gradient-to-r from-primary-600 to-secondary-600 p-8 text-center">
          <div className="flex justify-center mb-4">
            <Heart className="h-12 w-12 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">体重管理AI助手</h1>
          <p className="text-primary-100 mt-2">您的个人营养师+心理教练</p>
        </div>

        {/* 表单 */}
        <div className="p-8">
          <div className="flex mb-6">
            <button
              className={`flex-1 py-3 font-medium ${isLogin ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-600'}`}
              onClick={() => setIsLogin(true)}
            >
              登录
            </button>
            <button
              className={`flex-1 py-3 font-medium ${!isLogin ? 'bg-secondary-600 text-white' : 'bg-gray-100 text-gray-600'}`}
              onClick={() => setIsLogin(false)}
            >
              注册
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <>
                 <div>
                   <label className="block text-sm font-medium text-gray-700 mb-1">
                     用户名
                   </label>
                   <div className="relative">
                     <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                     <input
                       type="text"
                       name="username"
                       value={formData.username}
                       onChange={handleChange}
                       className={`w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                         errors.username ? 'border-red-500' : 'border-gray-300'
                       }`}
                       placeholder="请输入用户名（至少3个字符）"
                       required={!isLogin}
                       minLength={3}
                     />
                   </div>
                   {errors.username && (
                     <p className="mt-1 text-sm text-red-600">{errors.username}</p>
                   )}
                 </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    姓名（可选）
                  </label>
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="请输入姓名"
                  />
                </div>
              </>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                邮箱
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={`w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.email ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="请输入邮箱"
                  required
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                密码
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className={`w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.password ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="请输入密码（至少8位，包含大小写字母和数字）"
                  required
                  minLength={8}
                />
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password}</p>
              )}
            </div>

            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  确认密码
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                  <input
                    type="password"
                    name="confirm_password"
                    value={formData.confirm_password}
                    onChange={handleChange}
                    className={`w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                      errors.confirm_password ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="请再次输入密码"
                    required={!isLogin}
                    minLength={8}
                  />
                </div>
                {errors.confirm_password && (
                  <p className="mt-1 text-sm text-red-600">{errors.confirm_password}</p>
                )}
              </div>
            )}

            {!isLogin && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      年龄
                    </label>
                    <input
                      type="number"
                      name="age"
                      value={formData.age}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="岁"
                      min="0"
                      max="120"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      性别
                    </label>
                    <select
                      name="gender"
                      value={formData.gender}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    >
                      <option value="">请选择</option>
                      <option value="male">男</option>
                      <option value="female">女</option>
                      <option value="other">其他</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      身高 (cm)
                    </label>
                    <input
                      type="number"
                      name="height"
                      value={formData.height}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="厘米"
                      min="50"
                      max="250"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      当前体重 (kg)
                    </label>
                    <div className="relative">
                      <Scale className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                      <input
                        type="number"
                        name="initial_weight"
                        value={formData.initial_weight}
                        onChange={handleChange}
                        className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        placeholder="公斤"
                        step="0.1"
                        min="20"
                        max="300"
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    目标体重 (kg)
                  </label>
                  <div className="relative">
                    <Scale className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <input
                      type="number"
                      name="target_weight"
                      value={formData.target_weight}
                      onChange={handleChange}
                      className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="公斤"
                      step="0.1"
                      min="20"
                      max="300"
                    />
                  </div>
                </div>
              </>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-colors ${
                isLogin 
                  ? 'bg-primary-600 hover:bg-primary-700' 
                  : 'bg-secondary-600 hover:bg-secondary-700'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {isLoading ? '处理中...' : isLogin ? '登录' : '注册'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-600">
            {isLogin ? (
              <p>
                还没有账号？{' '}
                <button
                  onClick={() => setIsLogin(false)}
                  className="text-primary-600 hover:text-primary-700 font-medium"
                >
                  立即注册
                </button>
              </p>
            ) : (
              <p>
                已有账号？{' '}
                <button
                  onClick={() => setIsLogin(true)}
                  className="text-primary-600 hover:text-primary-700 font-medium"
                >
                  立即登录
                </button>
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Auth