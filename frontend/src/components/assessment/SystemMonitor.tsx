/**
 * 系统监控组件
 * 监控评估系统各服务的健康状态和性能指标
 */
import React, { useState, useEffect, useCallback } from 'react';
import { twMerge } from 'tailwind-merge';
import { assessmentService } from '../../services/AssessmentService';

export interface SystemMonitorProps {
  /** 是否自动刷新 */
  autoRefresh?: boolean;
  /** 刷新间隔（毫秒） */
  refreshInterval?: number;
  /** 自定义类名 */
  className?: string;
}

interface ServiceStatus {
  status: 'healthy' | 'unhealthy' | 'unknown';
  service: string;
  version?: string;
  active_sessions?: number;
  features?: string[];
  error?: string;
  response_time?: number;
}

interface SystemHealth {
  realTimeAssessment: ServiceStatus;
  reportGeneration: ServiceStatus;
  overall: 'healthy' | 'degraded' | 'down';
  lastChecked: Date;
}

/**
 * 系统监控组件
 */
const SystemMonitor: React.FC<SystemMonitorProps> = ({
  autoRefresh = true,
  refreshInterval = 30000, // 30秒
  className
}) => {
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  // 检查服务健康状态
  const checkServiceHealth = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const startTime = Date.now();

      // 并行检查所有服务
      const [realTimeResult, reportResult] = await Promise.allSettled([
        assessmentService.checkRealTimeAssessmentHealth(),
        assessmentService.checkReportServiceHealth()
      ]);

      const endTime = Date.now();

      // 处理实时评估服务结果
      const realTimeStatus: ServiceStatus = {
        status: 'unknown',
        service: 'real_time_assessment',
        response_time: endTime - startTime
      };

      if (realTimeResult.status === 'fulfilled') {
        realTimeStatus.status = realTimeResult.value.status || 'unknown';
        realTimeStatus.active_sessions = realTimeResult.value.active_sessions;
        realTimeStatus.version = realTimeResult.value.version;
      } else {
        realTimeStatus.status = 'unhealthy';
        realTimeStatus.error = realTimeResult.reason?.message || '服务不可用';
      }

      // 处理报告生成服务结果
      const reportStatus: ServiceStatus = {
        status: 'unknown',
        service: 'assessment_report',
        response_time: endTime - startTime
      };

      if (reportResult.status === 'fulfilled') {
        reportStatus.status = reportResult.value.status || 'unknown';
        reportStatus.features = reportResult.value.features;
        reportStatus.version = reportResult.value.version;
      } else {
        reportStatus.status = 'unhealthy';
        reportStatus.error = reportResult.reason?.message || '服务不可用';
      }

      // 计算整体健康状态
      let overallStatus: 'healthy' | 'degraded' | 'down' = 'healthy';
      
      if (realTimeStatus.status === 'unhealthy' && reportStatus.status === 'unhealthy') {
        overallStatus = 'down';
      } else if (realTimeStatus.status === 'unhealthy' || reportStatus.status === 'unhealthy') {
        overallStatus = 'degraded';
      }

      const health: SystemHealth = {
        realTimeAssessment: realTimeStatus,
        reportGeneration: reportStatus,
        overall: overallStatus,
        lastChecked: new Date()
      };

      setSystemHealth(health);
      setLastRefresh(new Date());

    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '健康检查失败';
      setError(errorMsg);
      console.error('系统健康检查失败:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 清理过期会话
  const cleanupSessions = useCallback(async () => {
    try {
      await assessmentService.cleanupExpiredSessions();
      // 清理后重新检查健康状态
      await checkServiceHealth();
    } catch (err) {
      console.error('清理会话失败:', err);
      setError('清理会话失败');
    }
  }, [checkServiceHealth]);

  // 自动刷新
  useEffect(() => {
    // 立即检查一次
    checkServiceHealth();

    if (!autoRefresh) return;

    const interval = setInterval(checkServiceHealth, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, checkServiceHealth]);

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'unhealthy':
        return 'text-red-600 bg-red-100';
      case 'degraded':
        return 'text-yellow-600 bg-yellow-100';
      case 'down':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  // 获取状态图标
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return '✅';
      case 'unhealthy':
        return '❌';
      case 'degraded':
        return '⚠️';
      case 'down':
        return '🔴';
      default:
        return '❓';
    }
  };

  // 格式化响应时间
  const formatResponseTime = (time?: number) => {
    if (!time) return 'N/A';
    return `${time}ms`;
  };

  return (
    <div className={twMerge('bg-white rounded-lg shadow-sm border border-gray-200', className)}>
      {/* 头部 */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900">系统监控</h3>
            <p className="text-sm text-gray-600">评估系统健康状态监控</p>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={cleanupSessions}
              disabled={isLoading}
              className="px-3 py-1 text-sm bg-yellow-100 text-yellow-700 rounded-md hover:bg-yellow-200 transition-colors duration-200 disabled:opacity-50"
            >
              🧹 清理会话
            </button>
            
            <button
              onClick={checkServiceHealth}
              disabled={isLoading}
              className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors duration-200 disabled:opacity-50"
            >
              {isLoading ? '🔄' : '🔄'} 刷新
            </button>
          </div>
        </div>
      </div>

      {/* 内容 */}
      <div className="p-6">
        {/* 错误提示 */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-md text-sm mb-4">
            {error}
          </div>
        )}

        {/* 加载状态 */}
        {isLoading && !systemHealth && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <span className="ml-2 text-gray-600">检查系统健康状态...</span>
          </div>
        )}

        {/* 系统健康状态 */}
        {systemHealth && (
          <div className="space-y-6">
            {/* 整体状态 */}
            <div className="text-center">
              <div className={twMerge(
                'inline-flex items-center px-4 py-2 rounded-full text-lg font-medium',
                getStatusColor(systemHealth.overall)
              )}>
                <span className="mr-2 text-2xl">{getStatusIcon(systemHealth.overall)}</span>
                系统状态: {systemHealth.overall === 'healthy' ? '正常' : 
                          systemHealth.overall === 'degraded' ? '部分异常' : '异常'}
              </div>
              
              {lastRefresh && (
                <p className="text-sm text-gray-500 mt-2">
                  最后检查: {lastRefresh.toLocaleString('zh-CN')}
                </p>
              )}
            </div>

            {/* 服务详情 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 实时评估服务 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-lg font-medium text-gray-900">实时评估服务</h4>
                  <span className={twMerge(
                    'px-2 py-1 rounded-full text-xs font-medium',
                    getStatusColor(systemHealth.realTimeAssessment.status)
                  )}>
                    {getStatusIcon(systemHealth.realTimeAssessment.status)} 
                    {systemHealth.realTimeAssessment.status === 'healthy' ? '正常' : '异常'}
                  </span>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">服务名称:</span>
                    <span className="font-medium">{systemHealth.realTimeAssessment.service}</span>
                  </div>
                  
                  {systemHealth.realTimeAssessment.version && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">版本:</span>
                      <span className="font-medium">{systemHealth.realTimeAssessment.version}</span>
                    </div>
                  )}
                  
                  {systemHealth.realTimeAssessment.active_sessions !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">活跃会话:</span>
                      <span className="font-medium">{systemHealth.realTimeAssessment.active_sessions}</span>
                    </div>
                  )}
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">响应时间:</span>
                    <span className="font-medium">{formatResponseTime(systemHealth.realTimeAssessment.response_time)}</span>
                  </div>

                  {systemHealth.realTimeAssessment.error && (
                    <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-red-700 text-xs">
                      错误: {systemHealth.realTimeAssessment.error}
                    </div>
                  )}
                </div>
              </div>

              {/* 报告生成服务 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-lg font-medium text-gray-900">报告生成服务</h4>
                  <span className={twMerge(
                    'px-2 py-1 rounded-full text-xs font-medium',
                    getStatusColor(systemHealth.reportGeneration.status)
                  )}>
                    {getStatusIcon(systemHealth.reportGeneration.status)} 
                    {systemHealth.reportGeneration.status === 'healthy' ? '正常' : '异常'}
                  </span>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">服务名称:</span>
                    <span className="font-medium">{systemHealth.reportGeneration.service}</span>
                  </div>
                  
                  {systemHealth.reportGeneration.version && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">版本:</span>
                      <span className="font-medium">{systemHealth.reportGeneration.version}</span>
                    </div>
                  )}
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">响应时间:</span>
                    <span className="font-medium">{formatResponseTime(systemHealth.reportGeneration.response_time)}</span>
                  </div>

                  {systemHealth.reportGeneration.features && (
                    <div className="mt-2">
                      <span className="text-gray-600 text-xs">功能特性:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {systemHealth.reportGeneration.features.map((feature, index) => (
                          <span key={index} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                            {feature}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {systemHealth.reportGeneration.error && (
                    <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-red-700 text-xs">
                      错误: {systemHealth.reportGeneration.error}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* 系统信息 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">系统信息</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">自动刷新:</span>
                  <span className="ml-1 font-medium">{autoRefresh ? '开启' : '关闭'}</span>
                </div>
                <div>
                  <span className="text-gray-600">刷新间隔:</span>
                  <span className="ml-1 font-medium">{refreshInterval / 1000}秒</span>
                </div>
                <div>
                  <span className="text-gray-600">检查时间:</span>
                  <span className="ml-1 font-medium">
                    {systemHealth.lastChecked.toLocaleTimeString('zh-CN')}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">系统版本:</span>
                  <span className="ml-1 font-medium">v1.0.0</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 无数据状态 */}
        {!systemHealth && !isLoading && !error && (
          <div className="text-center py-8">
            <div className="text-gray-400 text-6xl mb-4">📊</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">暂无监控数据</h3>
            <p className="text-gray-600">点击刷新按钮开始监控系统状态</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemMonitor; 