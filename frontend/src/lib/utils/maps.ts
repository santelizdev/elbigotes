export function getMapBounds(items: Array<{ latitude: number; longitude: number }>) {
  if (!items.length) {
    return null;
  }

  let south = items[0].latitude;
  let north = items[0].latitude;
  let west = items[0].longitude;
  let east = items[0].longitude;

  for (const item of items) {
    south = Math.min(south, item.latitude);
    north = Math.max(north, item.latitude);
    west = Math.min(west, item.longitude);
    east = Math.max(east, item.longitude);
  }

  return [
    [south, west],
    [north, east],
  ] as [[number, number], [number, number]];
}
