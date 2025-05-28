/**
 * 卡片组件
 * 用于展示内容的容器，提供统一的边框、阴影和内边距
 */
import React from 'react';
import { twMerge } from 'tailwind-merge';

export interface CardProps {
  /** 卡片内容 */
  children: React.ReactNode;
  /** 卡片标题 */
  title?: string;
  /** 卡片描述 */
  description?: string;
  /** 卡片底部内容 */
  footer?: React.ReactNode;
  /** 卡片头部右侧内容 */
  headerRight?: React.ReactNode;
  /** 是否无内边距 */
  noPadding?: boolean;
  /** 自定义类名 */
  className?: string;
  /** 卡片点击事件 */
  onClick?: () => void;
}

/**
 * 通用卡片组件
 * 用于内容展示，可以包含标题、描述和底部操作区
 */
const Card: React.FC<CardProps> = ({
  children,
  title,
  description,
  footer,
  headerRight,
  noPadding = false,
  className,
  onClick
}) => {
  const hasHeader = title || description || headerRight;
  
  return (
    <div 
      className={twMerge(
        'bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden',
        onClick && 'cursor-pointer hover:shadow-md transition-shadow',
        className
      )}
      onClick={onClick}
    >
      {/* 卡片头部 */}
      {hasHeader && (
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <div>
            {title && <h3 className="text-lg font-medium text-gray-900">{title}</h3>}
            {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
          </div>
          {headerRight && (
            <div className="ml-4">{headerRight}</div>
          )}
        </div>
      )}
      
      {/* 卡片内容 */}
      <div className={noPadding ? '' : 'p-6'}>
        {children}
      </div>
      
      {/* 卡片底部 */}
      {footer && (
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;
