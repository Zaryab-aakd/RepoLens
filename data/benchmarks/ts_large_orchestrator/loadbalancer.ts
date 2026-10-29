// Round robin load balancer
import { ServiceRegistry, ServiceNode } from "./registry.js";

export class LoadBalancer {
    private registry: ServiceRegistry;
    private cursor: number = 0;

    constructor(registry: ServiceRegistry) {
        this.registry = registry;
    }

    public getNextNode(): ServiceNode | null {
        const healthy = this.registry.getHealthyNodes();
        if (healthy.length === 0) return null;
        const node = healthy[this.cursor % healthy.length];
        this.cursor++;
        return node;
    }
}
