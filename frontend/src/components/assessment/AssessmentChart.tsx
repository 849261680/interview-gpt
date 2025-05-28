/**
 * 评估数据可视化组件
 * 提供雷达图、趋势图等多种图表展示评估数据
 */
import React, { useMemo } from 'react';
import { twMerge } from 'tailwind-merge';

export interface AssessmentChartProps {
  /** 维度评分数据 */
  dimensionScores: Record<string, number>;
  /** 评估历史数据 */
  assessmentHistory?: Array<{
    timestamp: string;
    overall_score: number;
    dimension_scores: Record<string, number>;
  }>;
  /** 图表类型 */
  chartType?: 'radar' | 'trend' | 'bar';
  /** 自定义类名 */
  className?: string;
}

/**
 * 评估数据可视化组件
 */
const AssessmentChart: React.FC<AssessmentChartProps> = ({
  dimensionScores,
  assessmentHistory = [],
  chartType = 'radar',
  className
}) => {
  // 格式化维度名称
  const formatDimensionName = (dimension: string): string => {
    const nameMap: Record<string, string> = {
      'technical_knowledge': '技术知识',
      'problem_solving': '问题解决',
      'code_quality': '代码质量',
      'system_design': '系统设计',
      'communication': '沟通能力',
      'professionalism': '职业素养',
      'culture_fit': '文化匹配',
      'career_planning': '职业规划',
      'teamwork': '团队协作',
      'leadership': '领导力',
      'adaptability': '适应能力',
      'stress_handling': '压力处理'
    };
    return nameMap[dimension] || dimension;
  };

  // 获取分数颜色
  const getScoreColor = (score: number): string => {
    if (score >= 90) return '#10b981'; // green-500
    if (score >= 80) return '#3b82f6'; // blue-500
    if (score >= 70) return '#f59e0b'; // yellow-500
    if (score >= 60) return '#f97316'; // orange-500
    return '#ef4444'; // red-500
  };

  // 雷达图数据处理
  const radarData = useMemo(() => {
    const dimensions = Object.keys(dimensionScores);
    const scores = Object.values(dimensionScores);
    
    if (dimensions.length === 0) return null;

    const angleStep = (2 * Math.PI) / dimensions.length;
    const centerX = 150;
    const centerY = 150;
    const maxRadius = 120;

    // 生成网格线
    const gridLevels = [20, 40, 60, 80, 100];
    const gridPaths = gridLevels.map(level => {
      const radius = (level / 100) * maxRadius;
      const points = dimensions.map((_, index) => {
        const angle = index * angleStep - Math.PI / 2;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);
        return `${x},${y}`;
      });
      return `M${points.join('L')}Z`;
    });

    // 生成轴线
    const axisLines = dimensions.map((_, index) => {
      const angle = index * angleStep - Math.PI / 2;
      const x = centerX + maxRadius * Math.cos(angle);
      const y = centerY + maxRadius * Math.sin(angle);
      return { x1: centerX, y1: centerY, x2: x, y2: y };
    });

    // 生成数据路径
    const dataPoints = scores.map((score, index) => {
      const angle = index * angleStep - Math.PI / 2;
      const radius = (score / 100) * maxRadius;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      return { x, y, score, dimension: dimensions[index] };
    });

    const dataPath = `M${dataPoints.map(p => `${p.x},${p.y}`).join('L')}Z`;

    // 生成标签位置
    const labels = dimensions.map((dimension, index) => {
      const angle = index * angleStep - Math.PI / 2;
      const labelRadius = maxRadius + 20;
      const x = centerX + labelRadius * Math.cos(angle);
      const y = centerY + labelRadius * Math.sin(angle);
      return {
        x,
        y,
        text: formatDimensionName(dimension),
        score: scores[index]
      };
    });

    return {
      gridPaths,
      axisLines,
      dataPath,
      dataPoints,
      labels,
      centerX,
      centerY
    };
  }, [dimensionScores]);

  // 趋势图数据处理
  const trendData = useMemo(() => {
    if (assessmentHistory.length === 0) return null;

    const width = 400;
    const height = 200;
    const padding = 40;

    const scores = assessmentHistory.map(h => h.overall_score);
    const minScore = Math.min(...scores);
    const maxScore = Math.max(...scores);
    const scoreRange = maxScore - minScore || 1;

    const points = assessmentHistory.map((history, index) => {
      const x = padding + (index / (assessmentHistory.length - 1)) * (width - 2 * padding);
      const y = height - padding - ((history.overall_score - minScore) / scoreRange) * (height - 2 * padding);
      return { x, y, score: history.overall_score, timestamp: history.timestamp };
    });

    const pathData = `M${points.map(p => `${p.x},${p.y}`).join('L')}`;

    return {
      points,
      pathData,
      width,
      height,
      minScore,
      maxScore
    };
  }, [assessmentHistory]);

  // 渲染雷达图
  const renderRadarChart = () => {
    if (!radarData) {
      return (
        <div className="flex items-center justify-center h-64">
          <p className="text-gray-500">暂无数据</p>
        </div>
      );
    }

    return (
      <div className="flex flex-col items-center">
        <svg width="300" height="300" className="overflow-visible">
          {/* 网格线 */}
          {radarData.gridPaths.map((path, index) => (
            <path
              key={index}
              d={path}
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="1"
            />
          ))}
          
          {/* 轴线 */}
          {radarData.axisLines.map((line, index) => (
            <line
              key={index}
              x1={line.x1}
              y1={line.y1}
              x2={line.x2}
              y2={line.y2}
              stroke="#d1d5db"
              strokeWidth="1"
            />
          ))}
          
          {/* 数据区域 */}
          <path
            d={radarData.dataPath}
            fill="rgba(59, 130, 246, 0.2)"
            stroke="#3b82f6"
            strokeWidth="2"
          />
          
          {/* 数据点 */}
          {radarData.dataPoints.map((point, index) => (
            <circle
              key={index}
              cx={point.x}
              cy={point.y}
              r="4"
              fill={getScoreColor(point.score)}
              stroke="white"
              strokeWidth="2"
            />
          ))}
          
          {/* 标签 */}
          {radarData.labels.map((label, index) => (
            <g key={index}>
              <text
                x={label.x}
                y={label.y}
                textAnchor="middle"
                dominantBaseline="middle"
                className="text-xs font-medium fill-gray-700"
              >
                {label.text}
              </text>
              <text
                x={label.x}
                y={label.y + 12}
                textAnchor="middle"
                dominantBaseline="middle"
                className="text-xs font-bold"
                fill={getScoreColor(label.score)}
              >
                {Math.round(label.score)}
              </text>
            </g>
          ))}
          
          {/* 中心点 */}
          <circle
            cx={radarData.centerX}
            cy={radarData.centerY}
            r="2"
            fill="#6b7280"
          />
        </svg>
      </div>
    );
  };

  // 渲染趋势图
  const renderTrendChart = () => {
    if (!trendData) {
      return (
        <div className="flex items-center justify-center h-64">
          <p className="text-gray-500">暂无历史数据</p>
        </div>
      );
    }

    return (
      <div className="flex flex-col items-center">
        <svg width={trendData.width} height={trendData.height}>
          {/* 背景网格 */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#f3f4f6" strokeWidth="1"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
          
          {/* 趋势线 */}
          <path
            d={trendData.pathData}
            fill="none"
            stroke="#3b82f6"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          
          {/* 数据点 */}
          {trendData.points.map((point, index) => (
            <g key={index}>
              <circle
                cx={point.x}
                cy={point.y}
                r="5"
                fill={getScoreColor(point.score)}
                stroke="white"
                strokeWidth="2"
              />
              <text
                x={point.x}
                y={point.y - 15}
                textAnchor="middle"
                className="text-xs font-medium fill-gray-700"
              >
                {Math.round(point.score)}
              </text>
            </g>
          ))}
          
          {/* Y轴标签 */}
          <text x="10" y="25" className="text-xs fill-gray-500">{trendData.maxScore}</text>
          <text x="10" y={trendData.height - 10} className="text-xs fill-gray-500">{trendData.minScore}</text>
        </svg>
        
        {/* 时间轴 */}
        <div className="flex justify-between w-full max-w-sm mt-2 text-xs text-gray-500">
          <span>开始</span>
          <span>当前</span>
        </div>
      </div>
    );
  };

  // 渲染柱状图
  const renderBarChart = () => {
    const dimensions = Object.keys(dimensionScores);
    const maxScore = Math.max(...Object.values(dimensionScores));

    if (dimensions.length === 0) {
      return (
        <div className="flex items-center justify-center h-64">
          <p className="text-gray-500">暂无数据</p>
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {dimensions.map((dimension) => {
          const score = dimensionScores[dimension];
          const percentage = (score / 100) * 100;
          
          return (
            <div key={dimension} className="space-y-1">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">
                  {formatDimensionName(dimension)}
                </span>
                <span 
                  className="text-sm font-bold"
                  style={{ color: getScoreColor(score) }}
                >
                  {Math.round(score)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="h-3 rounded-full transition-all duration-500 ease-out"
                  style={{
                    width: `${percentage}%`,
                    backgroundColor: getScoreColor(score)
                  }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className={twMerge('bg-white rounded-lg border border-gray-200 p-6', className)}>
      <div className="mb-4">
        <h3 className="text-lg font-medium text-gray-900">
          {chartType === 'radar' && '能力雷达图'}
          {chartType === 'trend' && '评分趋势图'}
          {chartType === 'bar' && '维度评分图'}
        </h3>
        <p className="text-sm text-gray-600">
          {chartType === 'radar' && '多维度能力分析'}
          {chartType === 'trend' && '评分变化趋势'}
          {chartType === 'bar' && '各维度详细评分'}
        </p>
      </div>

      <div className="flex justify-center">
        {chartType === 'radar' && renderRadarChart()}
        {chartType === 'trend' && renderTrendChart()}
        {chartType === 'bar' && renderBarChart()}
      </div>

      {/* 图例 */}
      <div className="mt-4 flex justify-center">
        <div className="flex items-center space-x-4 text-xs">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-green-500 rounded"></div>
            <span>优秀 (90+)</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-blue-500 rounded"></div>
            <span>良好 (80+)</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-yellow-500 rounded"></div>
            <span>一般 (70+)</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-orange-500 rounded"></div>
            <span>待提高 (60+)</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-red-500 rounded"></div>
            <span>需改进 (&lt;60)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssessmentChart; 