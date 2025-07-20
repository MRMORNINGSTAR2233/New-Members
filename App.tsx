
import React, { useEffect } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import { Layout } from "./components/Layout";
import { ThemeProvider } from "./contexts/ThemeContext";
import { GoogleIntegrationProvider } from "./contexts/GoogleIntegrationContext";
import { NotificationProvider } from "./contexts/NotificationContext";
import Dashboard from "./pages/Dashboard";
import Analytics from "./pages/Analytics";
import AdminDashboard from "./pages/AdminDashboard";
import Integrations from "./pages/Integrations";
import NotFound from "./pages/NotFound";
import Home from "./pages/LandingPage";
import { GlobalSearchPage } from "./pages/GlobalSearchPage";
import { ToolsPage } from "./pages/ToolsPage";
import { TalkPage } from "./pages/TalkPage";
import { ModelsPage } from "./pages/ModelsPage";
import { AppsPage } from "./pages/AppsPage";
import { OAuthCallbackHandler } from "./components/OAuthCallbackHandler";
import { AuthSuccessHandler } from "./components/AuthSuccessHandler";

const queryClient = new QueryClient();

const AppContent = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        navigate('/search');
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [navigate]);

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/search" element={<GlobalSearchPage />} />
      <Route path="/tools" element={<ToolsPage />} />
      
      {/* OAuth Callback routes */}
      <Route path="/auth/google/callback" element={<OAuthCallbackHandler />} />
      <Route path="/auth/slack/callback" element={<OAuthCallbackHandler />} />
      <Route path="/auth-success" element={<AuthSuccessHandler />} />

      {/* Dashboard with sidebar layout */}
      <Route path="/dashboard" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="talk" element={<TalkPage />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="integrations" element={<Integrations />} />
        <Route path="admin" element={<AdminDashboard />} />
        <Route path="workflows" element={<Dashboard />} />
        <Route path="knowledge" element={<AdminDashboard />} />
        <Route path="users" element={<AdminDashboard />} />
        <Route path="prompts" element={<Dashboard />} />
        <Route path="onboarding" element={<Dashboard />} />
      </Route>

      {/* Sidebar layout routes */}
      <Route path="/talk" element={<Layout />}>
        <Route index element={<TalkPage />} />
      </Route>

      <Route path="/models" element={<Layout />}>
        <Route path=":model" element={<ModelsPage />} />
      </Route>

      <Route path="/apps" element={<Layout />}>
        <Route path=":app" element={<AppsPage />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider>
      <NotificationProvider>
        <GoogleIntegrationProvider>
          <TooltipProvider>
            <Toaster />
            <Sonner />
            <BrowserRouter>
              <AppContent />
            </BrowserRouter>
          </TooltipProvider>
        </GoogleIntegrationProvider>
      </NotificationProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
