export function objMap(obj : object, fn: Function) {
    return Object.fromEntries(Object.entries(obj).map(([key, value]) => [key, fn(value, key)]));
}
