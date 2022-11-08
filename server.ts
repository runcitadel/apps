import { serve } from "https://deno.land/std@0.162.0/http/server.ts";
import { router } from "https://crux.land/router@0.0.12";

const handler = router({
  "GET@/": (_req) => new Response("Hello get!", { status: 200 }),
  "POST@/": (_req) => new Response("Hello post!", { status: 200 }),
});

console.log("Listening on http://localhost:8080");
await serve(handler);