// Expo reads app.json first, then this file, and this file wins where they
// overlap. app.json stays the human-readable base; this layer adds only what
// depends on the EAS project, which does not exist until the publish workflow
// creates it. The workflow exports EAS_PROJECT_ID after `eas init`; a plain
// `npx expo start` has no such variable and gets the base config unchanged.
//
// Deliberately absent: `runtimeVersion`. Expo Go can only load an update whose
// runtime is the SDK it was built for — EAS derives `exposdk:57.0.0` from the
// SDK when the field is left out, which is exactly the match Expo Go wants.
// `eas update:configure` would write an appVersion policy here and break that,
// so it is not run.
const base = require('./app.json');

module.exports = ({ config }) => {
  const projectId = process.env.EAS_PROJECT_ID;
  const merged = { ...base.expo, ...config };
  if (!projectId) return merged;
  return {
    ...merged,
    extra: { ...(merged.extra || {}), eas: { ...((merged.extra || {}).eas || {}), projectId } },
    updates: { ...(merged.updates || {}), url: 'https://u.expo.dev/' + projectId },
  };
};
