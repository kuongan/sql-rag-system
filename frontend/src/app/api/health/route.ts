import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

export async function GET() {
  try {
    // Check backend health
    const response = await fetch(`${BACKEND_URL}/health`, {
      method: 'GET',
    })
    
    if (!response.ok) {
      return NextResponse.json(
        { 
          status: 'error',
          message: 'Backend is not responding',
          backend_status: response.status
        },
        { status: 503 }
      )
    }
    
    const backendHealth = await response.json()
    
    return NextResponse.json({
      status: 'healthy',
      message: 'All systems operational',
      frontend: {
        status: 'ok',
        timestamp: new Date().toISOString()
      },
      backend: backendHealth,
      services: {
        next_api: 'ok',
        backend_connection: 'ok'
      }
    })
    
  } catch (error) {
    return NextResponse.json(
      { 
        status: 'error',
        message: 'Cannot connect to backend',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      },
      { status: 503 }
    )
  }
}