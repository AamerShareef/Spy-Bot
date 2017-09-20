// Copyright (c) 2015, Yaler GmbH, Switzerland
// All rights reserved

import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Iterator;
import java.util.TimeZone;

class YalerTunnel {
	static final Object
		CLIENT = 'c', SERVER = 's', PROXY = 'p',
		WRITING_REQUEST = 0, READING_RESPONSE = 1,
		READING_REQUEST = 2, WRITING_RESPONSE = 3, RELAYING = 4;
	static final String
		CONNECT = "CONNECT ",
		HTTP101 = "HTTP/1.1 101",
		HTTP200 = "HTTP/1.1 200",
		HTTP204 = "HTTP/1.1 204",
		HTTP307 = "HTTP/1.1 307",
		HTTP504 = "HTTP/1.1 504",
		HTTP_OK = "HTTP/1.1 200 OK\r\n\r\n",
		CONNECTION_FAILURE = "connection failure",
		UNEXPECTED_MESSAGE_LENGTH = "unexpected message length",
		UNEXPECTED_RELAY_RESPONSE = "unexpected relay response",
		UNEXPECTED_PROXY_RESPONSE = "unexpected proxy response",
		UNEXPECTED_PROXY_REQUEST = "unexpected proxy request";

	static String localHost, yalerHost;
	static int localPort, yalerPort;
	static String yalerUri;
	static Object mode;
	static boolean fatalError;
	static Selector selector;
	static int capacity, connectionCount, relayCount;

	static byte[] encode (String s) {
		try {
			return s.getBytes("US-ASCII");
		} catch (Exception e) { throw new Error(e); }
	}

	static ByteBuffer newReceiveBuffer (SocketChannel c) {
		try {
			return ByteBuffer.allocateDirect(c.socket().getReceiveBufferSize());
		} catch (Exception e) { throw new Error(e); }
	}

	static void shutdownOutput (SocketChannel c) {
		try {
			c.socket().shutdownOutput();
		} catch (Exception e) {}
	}

	static void close (SocketChannel c) {
		try {
			connectionCount--;
			c.close();
		} catch (Exception e) {}
	}

	static SocketChannel channel (SelectionKey k) {
		return (SocketChannel) k.channel();
	}

	static Object newAttachment (String host, int port, String uri,
		SelectionKey peer, ByteBuffer buffer, Object state)
	{
		return new Object[] {host, port, uri, peer, buffer, state};
	}

	static String host (SelectionKey k) {
		return (String) ((Object[]) k.attachment())[0];
	}

	static int port (SelectionKey k) {
		return (Integer) ((Object[]) k.attachment())[1];
	}

	static String uri (SelectionKey k) {
		return (String) ((Object[]) k.attachment())[2];
	}

	static SelectionKey peer (SelectionKey k) {
		return (SelectionKey) ((Object[]) k.attachment())[3];
	}

	static void setPeer (SelectionKey k, SelectionKey p) {
		((Object[]) k.attachment())[3] = p;
	}

	static ByteBuffer buffer (SelectionKey k) {
		return (ByteBuffer) ((Object[]) k.attachment())[4];
	}

	static void setBuffer (SelectionKey k, ByteBuffer b) {
		((Object[]) k.attachment())[4] = b;
	}

	static Object state (SelectionKey k) {
		return ((Object[]) k.attachment())[5];
	}

	static void setState (SelectionKey k, Object s) {
		((Object[]) k.attachment())[5] = s;
	}

	static boolean isInterestedIn (SelectionKey k, int ops) {
		return (k.interestOps() & ops) != 0;
	}

	static void include (SelectionKey k, int ops) {
		k.interestOps(k.interestOps() | ops);
	}

	static void exclude (SelectionKey k, int ops) {
		k.interestOps(k.interestOps() & ~ops);
	}

	static boolean startsWith (ByteBuffer b, int offset, int length, String s) {
		int k = 0;
		if (length >= s.length()) {
			while ((k != s.length()) && (s.charAt(k) == b.get(offset + k))) {
				k++;
			}
		}
		return k == s.length();
	}

	static int indexOf (ByteBuffer b, int offset, int length, String s) {
		int i = offset, j = offset, k = 0, p = offset, c = 0, x = 0;
		while ((k != s.length()) && (j != offset + length)) {
			if (i + k == j) {
				c = x = b.get(j);
				p = i;
				j++;
			} else if (i + k == j - 1) {
				c = x;
			} else {
				c = s.charAt(i + k - p);
			}
			if (s.charAt(k) == c) {
				k++;
			} else {
				k = 0;
				i++;
			}
		}
		return k == s.length()? j - k: -1;
	}

	static void openServer (String host, int port) {
		try {
			ServerSocketChannel c = ServerSocketChannel.open();
			c.configureBlocking(false);
			c.socket().setReuseAddress(true);
			c.socket().bind(new InetSocketAddress(host, port), 64);
			c.register(selector, SelectionKey.OP_ACCEPT);
		} catch (Exception e) { throw new Error(e); }
	}

	static SelectionKey server () {
		SelectionKey s = null;
		for (SelectionKey k: selector.keys()) {
			if (k.channel() instanceof ServerSocketChannel) {
				assert s == null;
				s = k;
			}
		}
		return s;
	}

	static void open (String host, int port, String uri, SelectionKey peer) {
		try {
			SocketChannel c = SocketChannel.open();
			c.configureBlocking(false);
			c.socket().setTcpNoDelay(true);
			c.connect(new InetSocketAddress(host, port));
			c.register(selector, SelectionKey.OP_CONNECT,
				newAttachment(host, port, uri, peer, newReceiveBuffer(c), null));
			connectionCount++;
		} catch (Exception e) { throw new Error(e); }
	}

	static void accept (SelectionKey k) {
		try {
			ServerSocketChannel s = (ServerSocketChannel) k.channel();
			SocketChannel c = s.accept();
			c.configureBlocking(false);
			c.socket().setTcpNoDelay(true);
			c.register(selector, 0,
				newAttachment(null, 0, null, null, newReceiveBuffer(c), null));
			connectionCount++;
			open(yalerHost, yalerPort, yalerUri, c.keyFor(selector));
		} catch (Exception e) { throw new Error(e); }
	}

	static String timestamp () {
		SimpleDateFormat f = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'");
		f.setTimeZone(TimeZone.getTimeZone("UTC"));
		return f.format(new Date());
	}

	static void handleError (SelectionKey k, String message) {
		System.out.println(
			timestamp() + ":" + message + ":" + host(k) + ":" + port(k));
		ByteBuffer b = buffer(k);
		int i = 0, j = b.position();
		while (i != j) {
			if ((i == 0) || (b.get(i - 1) == '\n')) {
				System.out.print('\t');
			}
			System.out.print((char) b.get(i));
			i++;
		}
		if ((i != 0) && (b.get(i - 1) != '\n')) {
			System.out.println();
		}
		close(channel(k));
		SelectionKey p = peer(k);
		if (p != null) {
			close(channel(p));
		}
	}

	static void beginRelaying (SelectionKey k) {
		SelectionKey p = peer(k);
		if (buffer(k).position() == 0) {
			include(k, SelectionKey.OP_READ);
		} else {
			buffer(k).flip();
			include(p, SelectionKey.OP_WRITE);
		}
		if (buffer(p).position() == 0) {
			include(p, SelectionKey.OP_READ);
		} else {
			buffer(p).flip();
			include(k, SelectionKey.OP_WRITE);
		}
		setState(p, RELAYING);
		setState(k, RELAYING);
		relayCount++;
	}

	static void prepareWriting (SelectionKey k, String s) {
		include(k, SelectionKey.OP_WRITE);
		ByteBuffer b = buffer(k);
		b.clear();
		b.put(encode(s));
		b.flip();
	}

	static String newRequest (String host, int port, String uri) {
		return
			mode == CLIENT?
				"CONNECT " + uri + " HTTP/1.1\r\n" +
				"Host: " + host + ":" + port + "\r\n\r\n":
			(mode == SERVER) || (mode == PROXY)?
				"POST " + uri + " HTTP/1.1\r\n" +
				"Upgrade: PTTH/1.0\r\n" +
				"Connection: Upgrade\r\n" +
				"Host: " + host + ":" + port + "\r\n\r\n":
			null;
	}

	static void connect (SelectionKey k) {
		SelectionKey p = peer(k);
		SocketChannel c = channel(k);
		try {
			c.finishConnect();
		} catch (Exception e) {}
		if (c.isConnected()) {
			if (p != null) {
				setPeer(p, k);
			}
			exclude(k, SelectionKey.OP_CONNECT);
			if ((mode == CLIENT) || (p == null)) {
				prepareWriting(k, newRequest(host(k), port(k), uri(k)));
				setState(k, WRITING_REQUEST);
			} else {
				assert (mode == SERVER) || (mode == PROXY);
				beginRelaying(k);
			}
		} else {
			handleError(k, CONNECTION_FAILURE);
		}
	}

	static void handleConnect (SelectionKey k) {
		exclude(k, SelectionKey.OP_READ);
		prepareWriting(k, HTTP_OK);
		setState(k, WRITING_RESPONSE);
	}

	static void handleSwitch (SelectionKey k) {
		if (connectionCount - relayCount < capacity / 2) {
			open(yalerHost, yalerPort, yalerUri, null);
		}
		if (mode == SERVER) {
			exclude(k, SelectionKey.OP_READ);
			open(localHost, localPort, null, k);
		} else {
			assert mode == PROXY;
			ByteBuffer b = buffer(k);
			int i = indexOf(b, 0, b.position(), "\r\n\r\n");
			if (i != -1) {
				i += "\r\n\r\n".length();
				if (startsWith(b, 0, i, CONNECT) && (i == b.position())) {
					handleConnect(k);
				} else {
					handleError(k, UNEXPECTED_PROXY_REQUEST);
				}
			} else {
				setState(k, READING_REQUEST);
			}
		}
	}

	static void handleRedirect (SelectionKey k) {
		ByteBuffer b = buffer(k);
		int i = indexOf(b, 0, b.position(), "\nLocation: http://");
		if (i != -1) {
			i += "\nLocation: http://".length();
			int j = b.position();
			StringBuilder host = new StringBuilder();
			int port = 80;
			while ((i != j) && (b.get(i) != ':') && (b.get(i) != '/')) {
				host.append((char) b.get(i));
				i++;
			}
			if ((i != j) && (b.get(i) == ':')) {
				i++;
				port = 0;
				while ((i != j) && (b.get(i) != '/')) {
					port = 10 * port + b.get(i) - '0';
					i++;
				}
			}
			if ((i != j) && (b.get(i) == '/')) {
				close(channel(k));
				open(host.toString(), port, uri(k), peer(k));
			} else {
				handleError(k, UNEXPECTED_RELAY_RESPONSE);
				fatalError = true;
			}
		} else {
			handleError(k, UNEXPECTED_RELAY_RESPONSE);
			fatalError = true;
		}
	}

	static void handleBuffer (SelectionKey k) {
		ByteBuffer b = buffer(k);
		int i = indexOf(b, 0, b.position(), "\r\n\r\n");
		if (i != -1) {
			i += "\r\n\r\n".length();
			if (state(k) == READING_RESPONSE) {
				if (startsWith(b, 0, i, HTTP307)) {
					b.position(i);
					handleRedirect(k);
				} else {
					if (mode == CLIENT) {
						if (startsWith(b, 0, i, HTTP200)) {
							exclude(k, SelectionKey.OP_READ);
							b.limit(b.position());
							b.position(i);
							b.compact();
							beginRelaying(k);
						} else {
							handleError(k, UNEXPECTED_PROXY_RESPONSE);
							fatalError = !startsWith(b, 0, i, HTTP504);
						}
					} else {
						assert (mode == SERVER) || (mode == PROXY);
						if (startsWith(b, 0, i, HTTP101)) {
							b.limit(b.position());
							b.position(i);
							b.compact();
							handleSwitch(k);
						} else if (startsWith(b, 0, i, HTTP204) && (i == b.position())) {
							exclude(k, SelectionKey.OP_READ);
							prepareWriting(k, newRequest(host(k), port(k), uri(k)));
							setState(k, WRITING_REQUEST);
						} else {
							handleError(k, UNEXPECTED_RELAY_RESPONSE);
							fatalError = true;
						}
					}
				}
			} else {
				assert (state(k) == READING_REQUEST) && (mode == PROXY);
				if (startsWith(b, 0, i, CONNECT) && (i == b.position())) {
					handleConnect(k);
				} else {
					handleError(k, UNEXPECTED_PROXY_REQUEST);
				}
			}
		} else if (!b.hasRemaining()) {
			handleError(k, UNEXPECTED_MESSAGE_LENGTH);
			fatalError = state(k) == READING_RESPONSE;
		}
	}

	static void read (SelectionKey k) {
		SelectionKey p = peer(k);
		SocketChannel c = channel(k);
		ByteBuffer b = buffer(k);
		int n = -1;
		try {
			n = c.read(b);
		} catch (Exception e) {}
		if (n > 0) {
			if (state(k) != RELAYING) {
				handleBuffer(k);
			} else {
				b.flip();
				exclude(k, SelectionKey.OP_READ);
				include(p, SelectionKey.OP_WRITE);
			}
		} else if (n == -1) {
			if (state(k) != RELAYING) {
				handleError(k, CONNECTION_FAILURE);
			} else {
				if (buffer(p) != null) {
					exclude(k, SelectionKey.OP_READ);
					setBuffer(k, null);
					shutdownOutput(channel(p));
				} else {
					close(channel(p));
					close(c);
					relayCount--;
				}
			}
		}
	}

	static void write (SelectionKey k) {
		SelectionKey p = peer(k);
		SocketChannel c = channel(k);
		ByteBuffer b = buffer(state(k) != RELAYING? k: p);
		int n = -1;
		try {
			n = c.write(b);
		} catch (Exception e) {}
		if (!b.hasRemaining()) {
			b.clear();
			exclude(k, SelectionKey.OP_WRITE);
			if (state(k) == WRITING_REQUEST) {
				include(k, SelectionKey.OP_READ);
				setState(k, READING_RESPONSE);
			} else if (state(k) == WRITING_RESPONSE) {
				assert mode == PROXY;
				open(localHost, localPort, null, k);
			} else {
				assert state(k) == RELAYING;
				include(p, SelectionKey.OP_READ);
			}
		} else if (n == -1) {
			if (state(k) != RELAYING) {
				handleError(k, CONNECTION_FAILURE);
			} else {
				if (buffer(k) != null) {
					exclude(k, SelectionKey.OP_WRITE);
					setBuffer(p, null);
				} else {
					close(channel(p));
					close(c);
					relayCount--;
				}
			}
		}
	}

	public static void main (String[] args) {
		if (args.length == 0) {
			System.err.print("YalerTunnel 1.1.1\n"
				+ "Usage: YalerTunnel (c | s | p) <local host>:<port> "
				+ "<yaler host>:<port> <yaler domain> [-capacity <capacity>]\n");
		} else {
			mode = args[0].charAt(0);
			String[] arg1 = args[1].split(":");
			localHost = arg1[0];
			localPort = Integer.parseInt(arg1[1]);
			String[] arg2 = args[2].split(":");
			yalerHost = arg2[0];
			yalerPort = Integer.parseInt(arg2[1]);
			yalerUri = "/" + args[3];
			if ((args.length >= 6) && args[4].equals("-capacity")) {
				capacity = Integer.parseInt(args[5]);
				if (capacity < 2) {
					throw new IllegalArgumentException();
				}
			} else {
				capacity = Integer.MAX_VALUE;
			}
			try {
				selector = Selector.open();
				if (mode == CLIENT) {
					openServer(localHost, localPort);
				}
				long cutoff = Long.MIN_VALUE;
				int previousConnectionCount = 0;
				do {
					if (mode == CLIENT) {
						if ((connectionCount <= capacity - 2)
							&& (previousConnectionCount > capacity - 2))
						{
							include(server(), SelectionKey.OP_ACCEPT);
						} else if ((connectionCount > capacity - 2)
							&& (previousConnectionCount <= capacity - 2))
						{
							exclude(server(), SelectionKey.OP_ACCEPT);
						}
						selector.select();
					} else {
						assert (mode == SERVER) || (mode == PROXY);
						if ((connectionCount == 2 * relayCount)
							&& (connectionCount <= capacity - 2))
						{
							long t = System.currentTimeMillis();
							if (t < cutoff) {
								selector.select(cutoff - t);
							} else {
								cutoff = t + 1000;
								open(yalerHost, yalerPort, yalerUri, null);
								selector.select();
							}
						} else {
							selector.select();
						}
					}
					previousConnectionCount = connectionCount;
					Iterator<SelectionKey> i = selector.selectedKeys().iterator();
					while (!fatalError && i.hasNext()) {
						SelectionKey k = i.next();
						if (k.isValid() && k.isAcceptable()) {
							accept(k);
						} else {
							if (k.isValid() && k.isConnectable()) {
								connect(k);
							}
							if (!fatalError && k.isValid() && k.isReadable()) {
								read(k);
							}
							if (!fatalError && k.isValid() && k.isWritable()) {
								write(k);
							}
						}
					}
					selector.selectedKeys().clear();
				} while (!fatalError);
			} catch (Exception e) { throw new Error(e); }
		}
	}
}
