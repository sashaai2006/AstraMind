{"class Snake {
  constructor(x, y, z) {
    this.x = x;
    this.y = y;
    this.z = z;
    this.length = 1;
    this.body = [[x, y, z]];
  }

  update() {
    this.body.unshift([this.x, this.y, this.z]);
    this.body.pop();
  }

  grow() {
    this.length++;
    this.body.push(this.body[this.body.length - 1]);
  }
}
}