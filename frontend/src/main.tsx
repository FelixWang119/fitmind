import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, FutureConfig } from 'react-router-dom'
import App from './App.tsx'
import './index.css'

const future: FutureConfig = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter future={future}>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
