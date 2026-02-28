import { Link, useParams, useSearchParams } from "react-router-dom";
import "../Styles/defaults.css";

const STATUS_TEXT = {
  400: "Bad Request",
  401: "Unauthorized",
  402: "Payment Required",
  403: "Forbidden",
  404: "Not Found",
  405: "Method Not Allowed",
  406: "Not Acceptable",
  407: "Proxy Authentication Required",
  408: "Request Timeout",
  409: "Conflict",
  410: "Gone",
  411: "Length Required",
  412: "Precondition Failed",
  413: "Payload Too Large",
  414: "URI Too Long",
  415: "Unsupported Media Type",
  416: "Range Not Satisfiable",
  417: "Expectation Failed",
  418: "I'm a teapot",
  421: "Misdirected Request",
  422: "Unprocessable Content",
  423: "Locked",
  424: "Failed Dependency",
  425: "Too Early",
  426: "Upgrade Required",
  428: "Precondition Required",
  429: "Too Many Requests",
  431: "Request Header Fields Too Large",
  451: "Unavailable For Legal Reasons",
  500: "Internal Server Error",
  501: "Not Implemented",
  502: "Bad Gateway",
  503: "Service Unavailable",
  504: "Gateway Timeout",
  505: "HTTP Version Not Supported",
  506: "Variant Also Negotiates",
  507: "Insufficient Storage",
  508: "Loop Detected",
  510: "Not Extended",
  511: "Network Authentication Required",
};

function normalizeStatusCode(value) {
  const parsed = Number.parseInt(value ?? "", 10);
  if (Number.isInteger(parsed) && parsed >= 100 && parsed <= 599) {
    return parsed;
  }

  return 500;
}

function getStatusGroup(code) {
  if (code >= 100 && code <= 199) {
    return "Informational response";
  }

  if (code >= 200 && code <= 299) {
    return "Success response";
  }

  if (code >= 300 && code <= 399) {
    return "Redirection response";
  }

  if (code >= 400 && code <= 499) {
    return "Client error response";
  }

  return "Server error response";
}

function getStatusMessage(code) {
  if (STATUS_TEXT[code]) {
    return STATUS_TEXT[code];
  }

  if (code >= 400 && code <= 499) {
    return "Unknown Client Error";
  }

  if (code >= 500 && code <= 599) {
    return "Unknown Server Error";
  }

  return "Unknown HTTP Status";
}

export default function StatusPage() {
  const { code: pathCode } = useParams();
  const [searchParams] = useSearchParams();
  const queryCode = searchParams.get("code");

  const statusCode = normalizeStatusCode(pathCode ?? queryCode);
  const message = getStatusMessage(statusCode);
  const group = getStatusGroup(statusCode);

  document.title = `${statusCode} ${message} • FluxMod`;

  return (
    <main className="container landing-main">
      <section className="page-card hero-stat">
        <p>
          <strong>{statusCode}</strong>{" "}
          <span id="protected-guilds-count">{message}</span>
        </p>
        <p className="muted">{group}</p>
      </section>

      <section
        className="page-card"
        style={{ width: "min(860px, 100%)", textAlign: "center" }}
      >
        <p className="muted">Try going back to the homepage.</p>
        <p>
          <Link className="nav-link active" to="/">
            Go Home
          </Link>
        </p>
      </section>
    </main>
  );
}