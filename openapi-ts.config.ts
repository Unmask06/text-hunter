import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: 'http://localhost:8000/openapi.json',
  output: 'frontend/src/client',
  plugins: [
    {
      name: '@hey-api/sdk',
      operations: {
        strategy: 'single',
        containerName: 'TextHunterClient',
      },
    },
  ],
});
