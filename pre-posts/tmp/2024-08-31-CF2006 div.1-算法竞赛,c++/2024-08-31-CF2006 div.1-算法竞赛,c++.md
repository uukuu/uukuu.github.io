[toc]

# CF2006 div.1

## B Iris and the Tree

原题目结点按 $\text{dfs}$ 序编号，那么每条边只会被两个询问覆盖，暴力修改统计即可。

记 $\text{cnt}$ 表示当前边还未全部出现的询问个数，$S$ 为当前出现的边权和，则现在的答案为 $(w-S)\times cnt + 2S$（考虑满的链直接记录总长，未满的链考虑每条边的贡献整理后得到此式）。

下面我们考虑一般情况，当结点编号任意或者给定树上的 $q$ 条链作为询问时。

不难发现我们仍可以用原题计算答案的方式，如果我们知道当前还没满的边的数量 $cnt$，已出现的边权和 $S$，已出现边的贡献 $sum$，那么答案为 $(w-S)\times cnt +sum$。

下面就来考虑如何求 $cnt$ 和 $sum$。

求 $sum$ 直接考虑每条边的贡献，即每条边被几个询问覆盖。我们可以对每条链求端点的 $\text{lca}$ 通过树上差分的方法求出。

求 $cnt$ 由于操作可以离线，我们可以定义边权为这条边出现的时间，通过树上倍增（边权下放点权，求链上最值）等方式就可以求出每条链上最晚出线的边的时间。进而得到每条边出现时会导致多少条链满了。

而且由于直接给出父亲，我们甚至不需要建出这棵树，因为倍增和差分都是自下而上更新的。

复杂度：$O(n\log n)$。

```cpp
const int N = 2e5 + 10;
int T, n, x[N], f[N][18], g[N][18], cf[N], cnt[N], dep[N];
ll w, y[N], S2, S;
void getlca(int x, int y, int &lca, int &mx)
{
	if (dep[x] < dep[y])
		swap(x, y);
	for (int p = 17; p >= 0; p--)
		if (dep[f[x][p]] >= dep[y])
			mx = max(mx, g[x][p]), x = f[x][p];
	if (x == y)
		return lca = x, void();
	for (int p = 17; p >= 0; p--)
		if (f[x][p] != f[y][p])
		{
			mx = max(mx, max(g[x][p], g[y][p]));
			x = f[x][p], y = f[y][p];
		}
	mx = max(mx, max(g[x][0], g[y][0]));
	return lca = f[x][0], void();
}
int main()
{
	read(T);
	while (T--)
	{
		read(n), read(w);
		for (int i = 1; i <= n; i++)
			cf[i] = cnt[i] = 0;
		for (int i = 2; i <= n; i++)
			read(f[i][0]), dep[i] = dep[f[i][0]] + 1;
		for (int j = 1; j <= 17; j++)
			for (int i = 1; i <= n; i++)
				f[i][j] = f[f[i][j - 1]][j - 1];
		for (int i = 2; i <= n; i++)
			read(x[i]), read(y[i]), g[x[i]][0] = i;
		for (int j = 1; j <= 17; j++)
			for (int i = 1; i <= n; i++)
				g[i][j] = max(g[f[i][j - 1]][j - 1], g[i][j - 1]);
		for (int i = 1, x, y, lca, mx; i <= n; i++)
		{
			x = i, y = i % n + 1;
			cf[x]++;
			cf[y]++;
			mx = 0;
			getlca(x, y, lca, mx);
			cf[lca] -= 2;
			cnt[mx]++;
		}
		for (int i = n; i; i--)
			cf[f[i][0]] += cf[i];
		S = S2 = 0;
		for (int i = 2, sum = n; i <= n; i++)
		{
			sum -= cnt[i];
			S += y[i];
			S2 += y[i] * cf[x[i]];
			write((w - S) * sum + S2, i < n ? ' ' : '\n');
		}
	}
	flushout();
	return 0;
}
```

## C Eri and Expanded Sets
### 题目大意{ignore = true}
对于集合 $S$ 现有操作，任选 $S$ 中的两个值不相同但奇偶性相同的数 $x$，$y$ 将 $\dfrac{x+y}{2}$ 加入 $S$。

我们称一个集合是‘好的’当且仅当这个集合中出现的数是连续的，即 $|S|=\max\limits_{x\in S}x - \min\limits_{x\in S} x + 1$。

现给定一个长为 $n$ 的序列 $\{a_i\}$ 求有多少个子区间 $[l,r]$ 满足将该区间的值取出作为初始 $S$，再进行若干次操作后能变为‘好的’集合。

### 题解{ignore = true}

如果两个数的差是偶数，我们就能在这两个数中间加入一个新数（之前不存在）。

手玩几组样例不难发现，经过若干次操作之后最终集合一定是一个公差为奇数的等差数列。

因为首先相邻数的差肯定是奇数，不然显然能继续加新数。

其次如果相邻的两个差不相等，不妨设 $x<y<z,y-x\neq z-y$ 那么对 $x,z$ 操作得到的数显然不是 $y$ 也能继续操作。

我们进一步观察相邻差不相等的操做，假设相邻的差分别为 $d_1<d_2$，那么新增一个数后这两个差将被分成 $d_1,\frac{d_2-d_1}{2},\frac{d_1+d_2}{2}$。

发现这个操作类似辗转相减法，只是多了个除以 $2$。但由于 $d_1,d_2$ 都是奇数，所以他们的 $\gcd$ 也是奇数，故 $\gcd(d_1,d_2)=\gcd(d_1,d_2-d_1)=\gcd(d_1,\frac{d_2-d_1}{2})$。

所以最终的公差就是排序后差分数组的 $\gcd$，又有排序的 $\gcd$ 等于乱序的 $\gcd$。

就是求 $\{a_i\}$ 的差分数组去除因子 $2$ 后，区间 $\gcd$ 等于 $1$ 的子区间数量。

当我们枚举左端点时，最左端的合法右端点显然是单调不降的，用双指针+线段树/st表维护区间 $\gcd$ 即可。

除此之外，当区间全相等时也是符合要求的但我们并没有记录，所以还需单独计算所有相等的子区间数量。

复杂度：$O(n(\log n+\log V))$
```cpp
const int N=4e5+10;
int T,n,a[N],tr[N<<2],d[N];
void build(int rt,int l,int r)
{
	if(l==r)return tr[rt]=d[l],void();
	int mid=(l+r)>>1;
	build(ls,l,mid);
	build(rs,mid+1,r);
	tr[rt]=__gcd(tr[ls],tr[rs]);
	return;
}
int res;
int query(int rt,int l,int r,int L,int R)
{
	if(L<=l&&r<=R)return tr[rt];
	int mid=(l+r)>>1;
	if(R<=mid)return query(ls,l,mid,L,R);
	if(mid<L)return query(rs,mid+1,r,L,R);
	return __gcd(query(ls,l,mid,L,R),query(rs,mid+1,r,L,R));
	
}
int main()
{
	read(T);
	while(T--)
	{
		read(n);
		for(int i=1;i<=n;i++)read(a[i]);
		for(int i=1;i<n;i++)
		{
			d[i]=abs(a[i+1]-a[i]);
			while(d[i]%2==0&&d[i])d[i]/=2;
		}
		if(n>1)build(1,1,n-1);
		ll ans=n;
		for(int i=1,r1=1,r2=0;i<n;i++)
		{
			r1=max(r1,i);
			while(r1<n&&query(1,1,n-1,i,r1)!=1)r1++;
			ans+=n-r1;
			r2=max(r2,i-1);
			while(r2<n-1&&d[r2+1]==0)r2++;
			ans+=r2-i+1;
		write(ans);
	}
	flushout();
	return 0;
}
```


## D Iris and Adjacent Products

### 题解{ignore=true}

考虑最优排序一定是大的一半倒序，小的一半正序交错排。

所以只要 $\forall i \le \sqrt{k}$ 满足大于 $\frac{n}{i}$ 的数的个数比小于 $i$ 的数少即可。（取等号的细节自行考虑）。

那么一个显然的想法就是直接开个 $n\sqrt{k}$ 的数组统计相应数的个数，但被卡空间了。

那么我们可以使用伟大的离线算法‘莫队’，这样我们只需一个 $\sqrt{k}$ 的数组统计个数即可。

也可以离线对每个 $i$ 都做一次。

复杂度：$O(n\sqrt{k})$

代码：咕咕咕。