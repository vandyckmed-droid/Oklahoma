// Expo reads app.json first, then this file, and this file wins where they
// overlap. app.json stays the human-readable base; this layer adds only what
// depends on the EAS project, which does not exist until the publish workflow
// creates it. The workflow exports EAS_PROJECT_ID after `eas init`; a plain
// `npx expo start` has no such variable and gets the base config unchanged.
//
// `runtimeVersion` uses the `sdkVersion` policy on purpose. Expo Go loads only
// updates whose runtime is the SDK it was built for, and this policy resolves
// to exactly that string — `exposdk:57.0.0` (verified with
// `npx expo-updates runtimeversion:resolve`). It has dropped out of the docs
// but @expo/config-plugins still implements it. Leaving the field out does
// NOT do this: the resolver returns null and eas-cli falls back to the app
// version ("1.0.0"), which Expo Go rejects — the first real publish did
// exactly that. `eas update:configure` would write an appVersion policy and
// break it the same way, so it is not run.
const base = require('./app.json');

module.exports = ({ config }) => {
  const projectId = process.env.EAS_PROJECT_ID;
  const merged = { ...base.expo, ...config, runtimeVersion: { policy: 'sdkVersion' } };
  if (!projectId) return merged;
  return {
    ...merged,
    extra: { ...(merged.extra || {}), eas: { ...((merged.extra || {}).eas || {}), projectId } },
    updates: { ...(merged.updates || {}), url: 'https://u.expo.dev/' + projectId },
  };
};
