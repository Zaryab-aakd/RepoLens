// Service registry
export interface ServiceNode {
    id: string;
    host: string;
    port: number;
    healthy: boolean;
}

export class ServiceRegistry {
    private nodes: Map<string, ServiceNode> = new Map();

    public register(node: ServiceNode): void {
        this.nodes.set(node.id, node);
    }

    public getHealthyNodes(): ServiceNode[] {
        return Array.from(this.nodes.values()).filter(n => n.healthy);
    }
}
