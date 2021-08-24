class Filter {
    public String name() {
      return getClass().getSimpleName();
    }
    public Waveform process(Waveform input) { return input; }
}

class Waveform {
    private static long counter;
    private final long id = counter++;
    public String toString() { return "Waveform " + id; }
}

class LowPass extends Filter {
    double cutoff;
    public LowPass(double cutoff) { this.cutoff = cutoff; }
    public Waveform process(Waveform input) {
      return input; // Dummy processing
    }
}

class HighPass extends Filter {
    double cutoff;
    public HighPass(double cutoff) { this.cutoff = cutoff; }
    public Waveform process(Waveform input) { return input; }
}

class BandPass extends Filter {
    double lowCutoff, highCutoff;
    public BandPass(double lowCut, double highCut) {
      lowCutoff = lowCut;
      highCutoff = highCut;
    }
    public Waveform process(Waveform input) { return input; }
}

class FilterAdapter implements Processor {
    Filter filter;
    public FilterAdapter(Filter filter) {
      this.filter = filter;
    }
    public String name() { return filter.name(); }
    public Waveform process(Object input) {
      return filter.process((Waveform)input);
    }
}	
  
public class FilterProcessor {
    public static void main(String[] args) {
      Waveform w = new Waveform();
      Apply.process(new FilterAdapter(new LowPass(1.0)), w);
      Apply.process(new FilterAdapter(new HighPass(2.0)), w);
      Apply.process(
        new FilterAdapter(new BandPass(3.0, 4.0)), w);
    }
}
