import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { MapPin, Calendar, Bell, Search, Star, Phone, Mail, Truck, Recycle, TreePine, Home, User, Settings, BarChart3, MessageCircle, Users, DollarSign, TrendingUp, Building2 } from 'lucide-react'
import './App.css'

// Mock data for demonstration
const mockSchedules = [
  {
    id: 1,
    type: 'Bulk Pickup',
    date: '2025-10-15',
    zone: 'Zone A',
    status: 'scheduled'
  },
  {
    id: 2,
    type: 'Yard Waste',
    date: '2025-10-18',
    zone: 'Zone A',
    status: 'scheduled'
  }
]

const mockBusinesses = [
  {
    id: 1,
    name: 'Green Cleanup Services',
    rating: 4.8,
    ratingCount: 127,
    distance: 2.3,
    services: ['Junk Removal', 'Yard Cleanup'],
    priceRange: '$$',
    responseTime: 'within 2 hours'
  },
  {
    id: 2,
    name: 'Rapid Trash Solutions',
    rating: 4.7,
    ratingCount: 89,
    distance: 3.1,
    services: ['Furniture Removal', 'Appliance Pickup'],
    priceRange: '$$$',
    responseTime: 'within 4 hours'
  },
  {
    id: 3,
    name: 'EcoWaste Pros',
    rating: 4.6,
    ratingCount: 156,
    distance: 4.2,
    services: ['Recycling', 'Hazardous Waste'],
    priceRange: '$',
    responseTime: 'same day'
  }
]

function App() {
  const [currentView, setCurrentView] = useState('homepage') // 'homepage', 'portal'
  const [userType, setUserType] = useState(null) // 'residential', 'professional', 'vendor'
  const [activeTab, setActiveTab] = useState('resident')
  const [searchAddress, setSearchAddress] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // Homepage Component
  const Homepage = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-blue-700 to-purple-800">
      {/* Navigation */}
      <nav className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-2">
              <div className="bg-white rounded-lg p-2">
                <Truck className="h-6 w-6 text-blue-600" />
              </div>
              <span className="text-white font-bold text-xl">BulkPickup Pro</span>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" className="text-white hover:bg-white/10">
                About
              </Button>
              <Button variant="ghost" className="text-white hover:bg-white/10">
                Contact
              </Button>
              <Button 
                className="bg-orange-500 hover:bg-orange-600 text-white"
                onClick={() => setCurrentView('portal')}
              >
                Sign In
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Never Miss Your
            <span className="block text-orange-400">Bulk Pickup Again</span>
          </h1>
          <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
            AI-powered scheduling platform connecting residents with pickup schedules and professional service providers nationwide
          </p>
          
          {/* User Type Selection */}
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-12">
            <Card 
              className="bg-white/10 backdrop-blur-md border-white/20 hover:bg-white/20 transition-all cursor-pointer transform hover:scale-105"
              onClick={() => {
                setUserType('residential')
                setCurrentView('portal')
              }}
            >
              <CardContent className="p-6 text-center">
                <Home className="h-12 w-12 text-orange-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">Residential User</h3>
                <p className="text-blue-100 text-sm">
                  Find pickup schedules for your address and connect with local service providers
                </p>
                <Button className="mt-4 bg-orange-500 hover:bg-orange-600 text-white w-full">
                  Get Started Free
                </Button>
              </CardContent>
            </Card>

            <Card 
              className="bg-white/10 backdrop-blur-md border-white/20 hover:bg-white/20 transition-all cursor-pointer transform hover:scale-105"
              onClick={() => {
                setUserType('professional')
                setCurrentView('portal')
              }}
            >
              <CardContent className="p-6 text-center">
                <Search className="h-12 w-12 text-orange-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">Professional User</h3>
                <p className="text-blue-100 text-sm">
                  Nationwide search capabilities and advanced monitoring for multiple properties
                </p>
                <Button className="mt-4 bg-orange-500 hover:bg-orange-600 text-white w-full">
                  Start Pro Trial
                </Button>
              </CardContent>
            </Card>

            <Card 
              className="bg-white/10 backdrop-blur-md border-white/20 hover:bg-white/20 transition-all cursor-pointer transform hover:scale-105"
              onClick={() => {
                setUserType('vendor')
                setCurrentView('portal')
              }}
            >
              <CardContent className="p-6 text-center">
                <Building2 className="h-12 w-12 text-orange-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">Service Provider</h3>
                <p className="text-blue-100 text-sm">
                  Grow your business with CRM, analytics, and nationwide lead generation
                </p>
                <Button className="mt-4 bg-orange-500 hover:bg-orange-600 text-white w-full">
                  Join Network
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-4 gap-6 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="bg-white/10 rounded-full p-4 w-16 h-16 mx-auto mb-3">
                <Calendar className="h-8 w-8 text-orange-400" />
              </div>
              <h4 className="text-white font-semibold mb-2">Smart Scheduling</h4>
              <p className="text-blue-100 text-sm">AI-powered pickup predictions and alerts</p>
            </div>
            <div className="text-center">
              <div className="bg-white/10 rounded-full p-4 w-16 h-16 mx-auto mb-3">
                <MapPin className="h-8 w-8 text-orange-400" />
              </div>
              <h4 className="text-white font-semibold mb-2">Nationwide Coverage</h4>
              <p className="text-blue-100 text-sm">Access schedules across all US municipalities</p>
            </div>
            <div className="text-center">
              <div className="bg-white/10 rounded-full p-4 w-16 h-16 mx-auto mb-3">
                <Users className="h-8 w-8 text-orange-400" />
              </div>
              <h4 className="text-white font-semibold mb-2">Service Network</h4>
              <p className="text-blue-100 text-sm">Connect with verified service providers</p>
            </div>
            <div className="text-center">
              <div className="bg-white/10 rounded-full p-4 w-16 h-16 mx-auto mb-3">
                <BarChart3 className="h-8 w-8 text-orange-400" />
              </div>
              <h4 className="text-white font-semibold mb-2">Business Analytics</h4>
              <p className="text-blue-100 text-sm">Performance tracking and insights</p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-white/5 backdrop-blur-md border-t border-white/10 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-blue-100">&copy; 2025 BulkPickup Pro. Powered by AI technology.</p>
        </div>
      </div>
    </div>
  )

  // Residential User Portal
  const ResidentialPortal = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => setCurrentView('homepage')}
            >
              ← Back
            </Button>
            <h1 className="text-xl font-bold">Residential Dashboard</h1>
          </div>
          <div className="flex items-center space-x-3">
            <Bell className="h-6 w-6 text-gray-600" />
            <User className="h-6 w-6 text-blue-600" />
          </div>
        </div>
      </div>

      <div className="p-4 space-y-6">
        {/* Search Bar */}
        <div className="relative">
          <MapPin className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
          <Input
            placeholder="Enter your address"
            value={searchAddress}
            onChange={(e) => setSearchAddress(e.target.value)}
            className="pl-10 py-3 text-lg"
          />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-3 gap-4">
          <Card className="text-center p-4 cursor-pointer hover:shadow-md transition-shadow">
            <Home className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <p className="text-sm font-medium">My Address</p>
          </Card>
          <Card className="text-center p-4 cursor-pointer hover:shadow-md transition-shadow">
            <Bell className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <p className="text-sm font-medium">Set Alert</p>
          </Card>
          <Card className="text-center p-4 cursor-pointer hover:shadow-md transition-shadow">
            <Search className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <p className="text-sm font-medium">Find Services</p>
          </Card>
        </div>

        {/* Recent Activity */}
        <div>
          <h2 className="text-lg font-semibold mb-3">Upcoming Pickups</h2>
          <div className="space-y-3">
            {mockSchedules.map((schedule) => (
              <Card key={schedule.id}>
                <CardContent className="p-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium">{new Date(schedule.date).toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}</p>
                      <p className="text-sm text-gray-600">{schedule.type}</p>
                    </div>
                    <Badge variant="secondary">{schedule.status}</Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Upgrade Prompt */}
        <Card className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
          <CardContent className="p-4">
            <h3 className="font-bold mb-2">Upgrade to Professional</h3>
            <p className="text-sm mb-3">Monitor multiple addresses nationwide with advanced features</p>
            <Button className="bg-white text-blue-600 hover:bg-gray-100">
              Upgrade Now
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  // Professional User Portal
  const ProfessionalPortal = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => setCurrentView('homepage')}
            >
              ← Back
            </Button>
            <h1 className="text-xl font-bold">Professional Dashboard</h1>
            <Badge className="bg-purple-100 text-purple-800">Pro Plan</Badge>
          </div>
          <div className="flex items-center space-x-3">
            <Bell className="h-6 w-6 text-gray-600" />
            <User className="h-6 w-6 text-purple-600" />
          </div>
        </div>
      </div>

      <div className="p-4 space-y-6">
        {/* Nationwide Search */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Search className="h-5 w-5" />
              <span>Nationwide Address Search</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative">
              <MapPin className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <Input
                placeholder="Search any address in the US..."
                className="pl-10 py-3 text-lg"
              />
            </div>
          </CardContent>
        </Card>

        {/* Multiple Address Monitoring */}
        <Card>
          <CardHeader>
            <CardTitle>Monitored Properties</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">123 Main St, Springfield, IL</p>
                  <p className="text-sm text-gray-600">Next pickup: Oct 15, 2025</p>
                </div>
                <Button size="sm" variant="outline">Manage</Button>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">456 Oak Ave, Chicago, IL</p>
                  <p className="text-sm text-gray-600">Next pickup: Oct 18, 2025</p>
                </div>
                <Button size="sm" variant="outline">Manage</Button>
              </div>
              <Button className="w-full" variant="outline">
                + Add New Property
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Advanced Analytics */}
        <Card>
          <CardHeader>
            <CardTitle>Portfolio Analytics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">12</div>
                <p className="text-sm text-gray-600">Properties Monitored</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">98%</div>
                <p className="text-sm text-gray-600">Pickup Success Rate</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  // Vendor User Portal
  const VendorPortal = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => setCurrentView('homepage')}
            >
              ← Back
            </Button>
            <h1 className="text-xl font-bold">Vendor Dashboard</h1>
            <Badge className="bg-green-100 text-green-800">Business Plan</Badge>
          </div>
          <div className="flex items-center space-x-3">
            <MessageCircle className="h-6 w-6 text-gray-600" />
            <Bell className="h-6 w-6 text-gray-600" />
            <User className="h-6 w-6 text-green-600" />
          </div>
        </div>
      </div>

      <div className="p-4 space-y-6">
        {/* Performance Metrics */}
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <DollarSign className="h-6 w-6 text-green-600 mx-auto mb-2" />
              <div className="text-2xl font-bold text-green-600">$4,250</div>
              <p className="text-sm text-gray-600">Monthly Revenue</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <Users className="h-6 w-6 text-blue-600 mx-auto mb-2" />
              <div className="text-2xl font-bold text-blue-600">47</div>
              <p className="text-sm text-gray-600">Active Leads</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <TrendingUp className="h-6 w-6 text-purple-600 mx-auto mb-2" />
              <div className="text-2xl font-bold text-purple-600">24%</div>
              <p className="text-sm text-gray-600">Conversion Rate</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <Star className="h-6 w-6 text-yellow-500 mx-auto mb-2" />
              <div className="text-2xl font-bold text-yellow-600">4.8</div>
              <p className="text-sm text-gray-600">Avg Rating</p>
            </CardContent>
          </Card>
        </div>

        {/* Service Area Management */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MapPin className="h-5 w-5" />
              <span>Service Area Management</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                <div>
                  <p className="font-medium">Springfield, IL (62701-62708)</p>
                  <p className="text-sm text-gray-600">23 active leads • $1,850 revenue</p>
                </div>
                <Button size="sm">Manage</Button>
              </div>
              <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                <div>
                  <p className="font-medium">Chicago, IL (60601-60610)</p>
                  <p className="text-sm text-gray-600">18 active leads • $2,400 revenue</p>
                </div>
                <Button size="sm">Manage</Button>
              </div>
              <Button className="w-full" variant="outline">
                + Add New Service Area
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* CRM & Lead Management */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5" />
              <span>Recent Leads</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="bg-blue-100 rounded-full p-2">
                    <User className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="font-medium">Sarah Johnson</p>
                    <p className="text-sm text-gray-600">Furniture removal • Springfield, IL</p>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Button size="sm" variant="outline">
                    <MessageCircle className="h-4 w-4" />
                  </Button>
                  <Button size="sm">Quote</Button>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="bg-green-100 rounded-full p-2">
                    <User className="h-4 w-4 text-green-600" />
                  </div>
                  <div>
                    <p className="font-medium">Mike Chen</p>
                    <p className="text-sm text-gray-600">Yard cleanup • Chicago, IL</p>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Button size="sm" variant="outline">
                    <MessageCircle className="h-4 w-4" />
                  </Button>
                  <Button size="sm">Quote</Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Analytics by Location */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>Performance by Location</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="font-medium">Springfield, IL</span>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">23 leads</span>
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-600 h-2 rounded-full" style={{width: '75%'}}></div>
                  </div>
                  <span className="text-sm font-medium">75%</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="font-medium">Chicago, IL</span>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">18 leads</span>
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div className="bg-green-600 h-2 rounded-full" style={{width: '85%'}}></div>
                  </div>
                  <span className="text-sm font-medium">85%</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-4">
          <Button className="h-12 bg-blue-600 hover:bg-blue-700">
            <Settings className="h-5 w-5 mr-2" />
            Update Profile
          </Button>
          <Button className="h-12 bg-green-600 hover:bg-green-700">
            <BarChart3 className="h-5 w-5 mr-2" />
            View Full Analytics
          </Button>
        </div>
      </div>
    </div>
  )

  // Main render logic
  if (currentView === 'homepage') {
    return <Homepage />
  }

  if (currentView === 'portal') {
    if (userType === 'residential') {
      return <ResidentialPortal />
    } else if (userType === 'professional') {
      return <ProfessionalPortal />
    } else if (userType === 'vendor') {
      return <VendorPortal />
    }
  }

  // Fallback to homepage
  return <Homepage />
}

export default App

