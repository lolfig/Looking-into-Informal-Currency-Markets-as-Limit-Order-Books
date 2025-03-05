def find_marginal_price(cp, dl, vp, ol):
        price = 0
        vol = 0

        for idxc in range(len(cp)):
            if idxc >= len(vp):
                break

            if cp[idxc] >= vp[idxc]:
                if dl[idxc] > ol[idxc]:
                    price = vp[idxc]
                    vol = ol[idxc]
                else:
                    price = vp[idxc]
                    vol = dl[idxc]
            else:
                break

        return price, vol