/**
 * Oklahoma — Expo Go client.
 *
 * This is a native shell around the generated page at web/index.html, not a
 * second implementation of the app. Every number Oklahoma shows is computed
 * once, in Python (oklahoma/metrics.py), committed to data/, and rendered
 * into web/index.html by the daily refresh workflow. A native rewrite would
 * have to re-implement fourteen metric formatters in JavaScript and would
 * drift the first time the Python side changed; this shell inherits the
 * calculations exactly, and keeps inheriting them.
 *
 * What the native layer adds, because a browser tab cannot:
 *   - a first-load state painted in the right theme, so there is no white
 *     flash into a dark page
 *   - offline and HTTP failure states with a retry, instead of a dead frame
 *   - the Android hardware back button driving in-page history
 *   - safe-area handling owned by the shell
 *   - outbound links opening in the system browser rather than trapping the
 *     viewer inside the app
 *
 * Expo Go safety: react-native-webview (13.16.1), react-native-safe-area-context
 * (5.7.0) and expo-status-bar are all in Expo SDK 57's bundledNativeModules,
 * so this runs in stock Expo Go with no development build.
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  BackHandler,
  Linking,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  View,
  useColorScheme,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { WebView } from 'react-native-webview';

/**
 * The published page. GitHub Pages serves the repository root, so this is the
 * same web/index.html the daily refresh workflow commits — the mobile app is
 * never a version behind the data.
 *
 * To point this at a branch preview instead, swap in the raw HTML URL for that
 * branch. To point it at a local `python -m http.server`, use your machine's
 * LAN address; Expo Go and the server have to be on the same network.
 */
const APP_URL = 'https://vandyckmed-droid.github.io/Oklahoma/web/';

/** Anything on this host stays in the app; everything else goes to the browser. */
const IN_APP_HOST = 'vandyckmed-droid.github.io';

/** Matches the web page's own two grounds, so the shell never flashes a
 *  different colour than the page it is about to show. */
const THEME = {
  light: { bg: '#ffffff', fg: '#1b1b1b', muted: '#6b6f74', line: '#d4d8dc', accent: '#00891c' },
  dark: { bg: '#000000', fg: '#ffffff', muted: '#a1a5a9', line: '#333333', accent: '#00c805' },
};

export default function App() {
  const scheme = useColorScheme() === 'dark' ? 'dark' : 'light';
  const c = THEME[scheme];

  const webRef = useRef(null);
  const canGoBack = useRef(false);
  const [loading, setLoading] = useState(true);
  const [failure, setFailure] = useState(null);
  // Bumping this remounts the WebView, which is the only reliable way to retry
  // a load that failed before the page existed to be reloaded.
  const [attempt, setAttempt] = useState(0);

  const retry = useCallback(() => {
    setFailure(null);
    setLoading(true);
    setAttempt((n) => n + 1);
  }, []);

  // Android's hardware back should walk the page's own history first, and only
  // leave the app once there is nothing left to go back to.
  useEffect(() => {
    if (Platform.OS !== 'android') return undefined;
    const sub = BackHandler.addEventListener('hardwareBackPress', () => {
      if (canGoBack.current && webRef.current) {
        webRef.current.goBack();
        return true;
      }
      return false;
    });
    return () => sub.remove();
  }, []);

  const onShouldStartLoadWithRequest = useCallback((request) => {
    const { url } = request;
    if (!url || url.startsWith('about:')) return true;
    if (url.startsWith('https://' + IN_APP_HOST)) return true;
    // A tap on an outbound link (the page footer's repository link, say)
    // belongs in the browser, not in a frame with no address bar or back button.
    Linking.openURL(url).catch(() => {});
    return false;
  }, []);

  return (
    <SafeAreaProvider>
      <SafeAreaView style={[styles.fill, { backgroundColor: c.bg }]} edges={['top', 'bottom', 'left', 'right']}>
        <StatusBar style={scheme === 'dark' ? 'light' : 'dark'} backgroundColor={c.bg} />

        {failure === null ? (
          <WebView
            key={attempt}
            ref={webRef}
            source={{ uri: APP_URL }}
            style={[styles.fill, { backgroundColor: c.bg }]}
            // The page is one self-contained document with inline JSON; nothing
            // it needs comes from another origin.
            originWhitelist={['https://*']}
            onShouldStartLoadWithRequest={onShouldStartLoadWithRequest}
            onNavigationStateChange={(navState) => {
              canGoBack.current = navState.canGoBack;
            }}
            onLoadEnd={() => setLoading(false)}
            onError={({ nativeEvent }) =>
              setFailure(nativeEvent.description || 'The page could not be loaded.')
            }
            onHttpError={({ nativeEvent }) =>
              setFailure('The server answered ' + nativeEvent.statusCode + '.')
            }
            // The watchlist and every display preference live in localStorage on
            // the page. Without this, Android drops them between launches.
            domStorageEnabled
            javaScriptEnabled
            // iOS gets pull-to-refresh and the edge-swipe back gesture for free;
            // Android has the hardware back button handled above.
            pullToRefreshEnabled
            allowsBackForwardNavigationGestures
            // Keeps a target="_blank" from opening a window with no way back.
            setSupportMultipleWindows={false}
            // The page sets its own colour-scheme meta; letting the WebView paint
            // white underneath produces a flash on every navigation in dark mode.
            backgroundColor={c.bg}
            overScrollMode="never"
            allowsInlineMediaPlayback
          />
        ) : (
          <View style={[styles.centre, { backgroundColor: c.bg }]}>
            <Text style={[styles.title, { color: c.fg }]}>Oklahoma is offline</Text>
            <Text style={[styles.body, { color: c.muted }]}>
              {failure}
              {'\n\n'}
              The page and its data are fetched from GitHub Pages, so this needs a
              connection. Everything you have starred is still on this device.
            </Text>
            <Pressable
              onPress={retry}
              style={({ pressed }) => [
                styles.button,
                { borderColor: c.line, opacity: pressed ? 0.6 : 1 },
              ]}
              accessibilityRole="button"
              accessibilityLabel="Try loading Oklahoma again"
            >
              <Text style={[styles.buttonText, { color: c.accent }]}>Try again</Text>
            </Pressable>
          </View>
        )}

        {loading && failure === null ? (
          <View style={[styles.overlay, { backgroundColor: c.bg }]} pointerEvents="none">
            <ActivityIndicator size="large" color={c.muted} />
            <Text style={[styles.loadingText, { color: c.muted }]}>Loading the universe…</Text>
          </View>
        ) : null}
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  fill: { flex: 1 },
  overlay: {
    position: 'absolute',
    top: 0,
    right: 0,
    bottom: 0,
    left: 0,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 14,
  },
  centre: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 32, gap: 16 },
  title: { fontSize: 22, fontWeight: '700', letterSpacing: -0.4 },
  body: { fontSize: 15, lineHeight: 22, textAlign: 'center' },
  loadingText: { fontSize: 14 },
  button: { borderWidth: 1, borderRadius: 12, paddingVertical: 13, paddingHorizontal: 22, marginTop: 6 },
  buttonText: { fontSize: 15, fontWeight: '600' },
});
