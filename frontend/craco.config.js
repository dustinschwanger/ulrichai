const CracoEsbuildPlugin = require('craco-esbuild');

module.exports = {
  plugins: [
    {
      plugin: CracoEsbuildPlugin,
      options: {
        esbuildMinimizerOptions: {
          target: 'es2015',
          css: true,
        },
      },
    },
  ],
  webpack: {
    configure: (webpackConfig) => {
      // Increase memory limit for build
      webpackConfig.optimization = {
        ...webpackConfig.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name(module) {
                // Get the package name
                if (!module.context) return 'vendor.shared';
                const match = module.context.match(
                  /[\\/]node_modules[\\/](.*?)([\\/]|$)/
                );
                if (!match) return 'vendor.shared';
                const packageName = match[1];
                return `vendor.${packageName.replace('@', '')}`;
              },
              priority: 10,
            },
            mui: {
              test: /[\\/]node_modules[\\/]@mui[\\/]/,
              name: 'vendor.mui',
              priority: 20,
            },
            tiptap: {
              test: /[\\/]node_modules[\\/]@tiptap[\\/]/,
              name: 'vendor.tiptap',
              priority: 20,
            },
            redux: {
              test: /[\\/]node_modules[\\/](@reduxjs|react-redux)[\\/]/,
              name: 'vendor.redux',
              priority: 20,
            },
            common: {
              minChunks: 2,
              priority: 5,
              reuseExistingChunk: true,
            },
          },
        },
      };

      // Reduce bundle size
      if (process.env.NODE_ENV === 'production') {
        webpackConfig.optimization.minimize = true;
        webpackConfig.devtool = false;
      }

      return webpackConfig;
    },
  },
};
