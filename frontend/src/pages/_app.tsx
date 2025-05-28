import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import Head from 'next/head';

/**
 * 应用入口组件
 * 负责全局布局和样式加载
 */
export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="description" content="AI模拟面试平台，多AI AGENT面试系统" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <Component {...pageProps} />
    </>
  );
}
