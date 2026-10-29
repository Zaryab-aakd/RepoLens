// Orchestration app
import { ServiceRegistry } from "./registry.js";
import { LoadBalancer } from "./loadbalancer.js";

export function bootstrapCluster(): LoadBalancer {
    const reg = new ServiceRegistry();
    reg.register({ id: "srv-1", host: "10.0.0.1", port: 8080, healthy: true });
    reg.register({ id: "srv-2", host: "10.0.0.2", port: 8080, healthy: true });
    return new LoadBalancer(reg);
}
