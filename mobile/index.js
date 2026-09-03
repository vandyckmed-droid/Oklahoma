import { registerRootComponent } from 'expo';

import App from './App';

// registerRootComponent wires the root component up for both Expo Go and a
// native build, so the same entry point serves the Snack and a local run.
registerRootComponent(App);
