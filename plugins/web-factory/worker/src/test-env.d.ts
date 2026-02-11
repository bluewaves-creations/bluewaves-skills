import type { Env } from "./auth";

declare module "cloudflare:test" {
  interface ProvidedEnv extends Env {}
}
