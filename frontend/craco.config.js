module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Find and disable the ForkTsCheckerWebpackPlugin to prevent memory issues
      const forkTsCheckerIndex = webpackConfig.plugins.findIndex(
        (plugin) => plugin.constructor.name === 'ForkTsCheckerWebpackPlugin'
      );

      if (forkTsCheckerIndex !== -1) {
        // Remove the plugin entirely to avoid memory issues
        webpackConfig.plugins.splice(forkTsCheckerIndex, 1);
      }

      return webpackConfig;
    },
  },
  eslint: {
    enable: false, // Disable ESLint to reduce memory usage
  },
  typescript: {
    enableTypeChecking: false, // Disable type checking during build
  },
};
